import re
from bs4 import BeautifulSoup
from util.Episode import Episode
from util.Color import printer
from scrapers.base_scraper import BaseScraper


class RyuAnimeScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, is_dub=False):
        """Ryuanime scraper to collect direct download links.

        Sources
        -------
        TrollVid
        MP4Upload

        """
        super().__init__(url, start_episode, end_episode, session, gui)
        self.is_dub = is_dub

    def __extract_episodes_div(self, soup_page):
        div_row = soup_page.find("div", attrs={"class": "card-body"}).find("div", attrs={"class": "row"})

        for div_col in div_row.findAll("div"):
            # there are 2 columns one is subbed, the other is dubbed
            is_dub = True if div_col.text.lower() == "dubbed" else False
            if self.is_dub is is_dub:
                return div_col

        return None

    def __extract_page_urls(self):
        printer("INFO", "Extracting Page URLs...", self.gui)
        page = self.get_url_content()

        soup_html = BeautifulSoup(page.content, "html.parser")
        episodes_div = self.__extract_episodes_div(soup_html)

        if episodes_div is not None:
            episodes_list = episodes_div.findAll("li")
            for episode_item in episodes_list:
                epi_anch = episode_item.find("a", href=True)
                epi_no = int(re.search(r'(\d+)', epi_anch.text).group(1))

                if epi_no < self.start_episode or epi_no > self.end_episode:
                    continue

                title = "Episode - {no}".format(no=str(epi_no))

                episode = Episode(title, title)
                episode.page_url = epi_anch["href"]

                self.episodes.append(episode)

    def __get_direct_url(self, page, page_url):
        """Extracting video source links.

        Args
        -------
        page (str): HTML source page

        Returns
        -------
        url: A direct link to download the video from either Trollvid /MP4Upload, or None if neither is available

        """
        matches = re.findall(r'\"host\":\"(\w+)\",\"id\":\"(\w+)\",\"type\":\"(\w+)\"', page)

        head = {
            "referer": page_url
        }

        for match in matches:
            host = match[0]
            vid_id = match[1]
            # vid_type = match[2]

            if host == "trollvid":
                troll_page_url = "https://trollvid.net/embed/{v_id}".format(v_id=vid_id)
                troll_page = self.session.get(troll_page_url, headers=head).text

                src_tag = re.search(r'<source\s+src=\"(\S+)\"\s+type=\"video/mp4\">', troll_page)

                if src_tag is not None:
                    return src_tag.group(1)
                else:
                    print("trollvid source not found!")

            elif host == "mp4upload":
                # for now mp4upload page came "deleted" for tested sources. Will check and update later
                # mpu_page_url = "https://www.mp4upload.com/embed-{v_id}.html".format(v_id=vid_id)
                # mpu_page = self.session.get(mpu_page_url, headers=head).text
                pass

        return None

    def __extract_download_urls(self):
        printer("INFO", "Setting direct links...", self.gui)
        for episode in self.episodes:
            page = self.session.get(episode.page_url).text
            # get video links for mp4upload and trollvideo
            direct_link = self.__get_direct_url(page, episode.page_url)

            if direct_link is not None:
                episode.download_url = direct_link
            else:
                printer("ERROR", "Download link not found for {ep}".format(ep=episode.episode), self.gui)

    def get_direct_links(self):
        self.__extract_page_urls()
        if len(self.episodes) > 0:
            self.__extract_download_urls()
            return self.episodes

        return None

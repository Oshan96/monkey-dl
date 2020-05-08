import re
from bs4 import BeautifulSoup
from util.Episode import Episode
from scrapers.base_scraper import BaseScraper
from util.Color import printer


class AnimeFreakScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, is_dub=False):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.is_dub = is_dub

    def __extract_source_links(self, page_content):
        link_sources = [match.group(1) for match in
                        re.finditer("file\s*:\s*[\"\']\s*([htps][^\"\']+)", page_content)]

        return link_sources

    def __set_download_link(self, episode):
        response = ""
        if not self.is_dub:
            print("sub")
            response = self.session.get(episode.page_url)
            if response.status_code != 200:
                print("checking subbed mirror")
                response = self.session.get(episode.page_url + "/2")

        else:
            print("dub")
            response = self.session.get(episode.page_url + "/3")
            if response.status_code != 200:
                print("checking dubbed mirror")
                response = self.session.get(episode.page_url + "/4")

        sources = self.__extract_source_links(response.text)
        if len(sources) > 0:
            for source in sources:
                if ".mp4" in source:
                    episode.download_url = source
                    return True

        return False

    def __collect_episodes(self):
        printer("INFO", "Extracting page URLs...", self.gui)
        episodes = []
        response = self.session.get(self.url)
        if response.status_code == 200:
            soup_html = BeautifulSoup(response.content, "html.parser")
            epi_tags = soup_html.findAll("ul", attrs={"class": "check-list"})[1].findAll("a", href=True)

            for epi_tag in epi_tags:
                href = epi_tag["href"]
                # print(href)
                epi_no = int(href.split("-")[-1])
                # print(epi_no)

                if epi_no < self.start_episode or epi_no > self.end_episode:
                    continue

                episode = Episode("Episode - " + str(epi_no), "Episode - " + str(epi_no))
                episode.page_url = href

                try:
                    res = self.__set_download_link(episode)
                    if res:
                        episodes.append(episode)
                    else:
                        printer("ERROR", "Failed to collect download link for "+episode.title, self.gui)

                except Exception as ex:
                    printer("ERROR", str(ex), self.gui)

        return episodes

    def get_direct_links(self):
        try:
            episodes = self.__collect_episodes()
            if len(episodes) > 0:
                return episodes
            else:
                return None

        except Exception as ex:
            printer("ERROR", str(ex), self.gui)
            return None

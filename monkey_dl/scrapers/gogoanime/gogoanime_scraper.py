import re
from util.Episode import Episode
from bs4 import BeautifulSoup
from extractors.jwplayer_extractor import JWPlayerExtractor
from scrapers.base_scraper import BaseScraper
from util.Color import printer


class GoGoAnimeScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, resolution="480"):
        super().__init__(url, start_episode, end_episode, session, gui)
        if self.url.endswith("/"):
            self.url = self.url[:-1]

        self.resolution = resolution
        self.extractor = JWPlayerExtractor(None, self.session)
        self.anime_id = None
        self.api_link_bases = ['https://ajax.gogocdn.net/ajax/load-list-episode',
                               'https://ajax.apimovie.xyz/ajax/load-list-episode']

        if "gogoanime.video" in self.url:
            self.domain_name = ".gogoanime.video"
            # self.host = "www2.gogoanime.video"
        elif "gogoanime.io" in self.url:
            self.domain_name = "www18.gogoanime.io"

        self.__set_anime_id()

    def __set_anime_id(self):
        print("Setting anime_id")
        response = self.request_from_cookies().content
        soup_html = BeautifulSoup(response, "html.parser")
        # print(soup_html)
        movie_id_tag = soup_html.find("input", attrs={"id": "movie_id"})
        # print(movie_id_tag)
        if movie_id_tag is not None:
            self.anime_id = movie_id_tag["value"]

    def __get_episode_data(self):
        print("getting episode data")
        for base_link in self.api_link_bases:
            api_link = base_link + "?ep_start=" + str(self.start_episode) + "&ep_end=" + str(
                self.end_episode) + "&id=" + self.anime_id

            # print("api link : ", api_link)
            if "apimovie.xyz" in base_link:
                response = self.request_from_cookies(api_link, domain_name=".apimovie.xyz")
                # print(response)
            else:
                response = self.request_from_cookies(api_link, domain_name=".gogocdn.net")
            # print(response)
            if response.status_code == 200:
                return response.content

        return None

    def __get_page_url(self, href):
        base_url = re.search(r"(.*)/category/", self.url).group(1)
        # print(base_url)
        src = base_url + href
        # print(src)

        return src

    def __set_stream_url(self, episode):
        # print(episode.page_url)
        response = self.request_from_cookies(episode.page_url, referer=self.url)
        if response.status_code == 200:
            soup_html = BeautifulSoup(response.content, "html.parser")
            item_tag = soup_html.find("li", attrs={"class": "anime"}).find("a")
            streamer_url = item_tag["data-video"]
            if "https" not in streamer_url:
                streamer_url = "https:" + streamer_url

            # print("streamer url :", streamer_url)
            streamer_resp = self.session.get(streamer_url)
            # print("Streamer resp :", streamer_resp)
            if streamer_resp.status_code == 200:
                sources = self.extractor.extract_sources(streamer_resp.text)
                src = ""
                for source in sources:
                    if "m3u8" in source:
                        src = source
                        break
                # print("src :", src)
                if src != "":
                    res_link_id = self.extractor.get_resolution_link(src, self.resolution)
                    stream_base = re.search(r"(.*)/[\S]+\.m3u8", src).group(1)
                    episode.download_url = stream_base + "/" + res_link_id
                    print("stream url:", episode.download_url)

                    return True

        return False

    def __collect_episodes(self):
        printer("INFO", "Extracting page URLs...", self.gui)
        episodes = []
        if self.anime_id is not None:
            data = self.__get_episode_data()
            if data is not None:
                soup_html = BeautifulSoup(data, "html.parser")
                anchor_tags = soup_html.findAll("a", href=True)
                for anchor in anchor_tags:
                    href = anchor["href"].strip()
                    epi_no = int(href.split("-")[-1])

                    if epi_no < self.start_episode or epi_no > self.end_episode:
                        continue

                    episode = Episode("Episode - " + str(epi_no), "Episode - " + str(epi_no))
                    episode.is_direct = False
                    episode.page_url = self.__get_page_url(href)
                    # print(episode.page_url)
                    val = self.__set_stream_url(episode)
                    if val:
                        episodes.append(episode)
                    else:
                        printer("ERROR", "Failed to collect download link for " + episode.title, self.gui)

        else:
            print("Anime id is None")

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


# if __name__ == "__main__":
#     import requests
#     import traceback
#
#     s = requests.Session()
#
#     epis = GoGoAnimeScraper("https://www18.gogoanime.io/category/one-piece", 300, 300, s).get_direct_links()
#
#     try:
#         for epi in epis:
#             print(epi.episode)
#             print(epi.title)
#             print(epi.download_url)
#             print("-" * 25)
#             print()
#     except Exception:
#         print(traceback.format_exc())

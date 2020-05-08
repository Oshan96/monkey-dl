import re
import traceback
from scrapers.base_scraper import BaseScraper
from util.Episode import Episode
from extractors.jwplayer_extractor import JWPlayerExtractor


class AnimeFlixScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, resolution="720", is_dub=False):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.resolution = resolution
        self.is_dub = is_dub
        url_data = re.search("(.*)/shows/(.*)", self.url)
        self.url_base = url_data.group(1)
        self.slug = url_data.group(2).split("/")[0]
        self.extractor = JWPlayerExtractor(None, None)

        self.anime_id = None
        self.__set_anime_id()

    def __set_anime_id(self):
        api_url = "{base}/api/anime/detail?slug={slug}".format(base=self.url_base, slug=self.slug)
        data = self.session.get(api_url).json()
        self.anime_id = data["data"]["id"]

    def __get_start_end_page(self):
        limit = 50

        api_url = "{base}/api/episodes?anime_id={id}&limit={limit}".format(base=self.url_base, id=self.anime_id,
                                                                           limit=str(limit))
        data = self.session.get(api_url).json()

        last_page = data["meta"]["last_page"]

        start_page = ((self.start_episode - 1) // limit) + 1
        end_page = ((self.end_episode - 1) // limit) + 1

        if end_page > last_page:
            end_page = last_page

        return start_page, last_page, limit

    def __set_download_link(self, episode):
        api_url = "{base}/api/videos?episode_id={id}".format(base=self.url_base, id=str(episode.id))
        url_data = self.session.get(api_url).json()
        for src_data in url_data:
            if self.is_dub:
                if src_data["lang"] == "dub" and src_data["type"] != "hls":
                    episode.download_url = src_data["file"]
                    return
            else:
                if src_data["lang"] == "sub" and src_data["hardsub"] and src_data["type"] == "hls":
                    master = src_data["file"]
                    # print("master")
                    # print(master)
                    res_stream_link = self.extractor.get_resolution_link(master, self.resolution)
                    episode.download_url = res_stream_link
                    episode.is_direct = False
                    return

    def __collect_episodes(self):
        if self.anime_id is None:
            return None

        episodes = []

        start_page, end_page, limit = self.__get_start_end_page()
        curr_page = start_page
        while curr_page <= end_page:
            api_url = "{base}/api/episodes?anime_id={id}&limit={limit}&page={page}".format(base=self.url_base,
                                                                                           id=self.anime_id,
                                                                                           limit=str(limit),
                                                                                           page=str(curr_page))
            curr_page += 1

            api_data = self.session.get(api_url).json()
            for epi in api_data["data"]:
                epi_no = int(epi["episode_num"])

                if epi_no < self.start_episode or epi_no > self.end_episode:
                    continue

                if self.is_dub and epi["dub"] == 0:
                    print("No dubbed version for Episode - {epi}".format(epi=str(epi_no)))
                    continue

                title = epi["title"]
                id = epi["id"]
                episode = Episode(title, "Episode - {epi}".format(epi=str(epi_no)))
                episode.id = id

                self.__set_download_link(episode)

                episodes.append(episode)

        return episodes

    def get_direct_links(self):
        try:
            episodes = self.__collect_episodes()
            return episodes
        except Exception as ex:
            trace = traceback.format_exc()
            print(trace)
            return None

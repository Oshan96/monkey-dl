import re
from bs4 import BeautifulSoup
from util.Episode import Episode
from scrapers.base_scraper import BaseScraper
from util.Color import printer
from extractors.kwik_extractor import KwikExtractor


class AnimePaheScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, resolution="720", is_filler=True):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.resolution = resolution
        self.is_filler = is_filler
        self.id = None
        self.base_url = "https://animepahe.com"
        self.start_page = 1
        self.end_page = 1
        self.extractor = KwikExtractor(session, gui)

        self.__set_working_url()
        self.__set_anime_id()
        self.__set_start_end_page()

    def __set_working_url(self):
        page = self.session.get(self.url).content
        soup_page = BeautifulSoup(page, "html.parser")
        og_url = soup_page.find("meta", attrs={"property": "og:url"})
        if og_url is not None:
            self.url = og_url["content"]

    def __set_anime_id(self):
        page = self.session.get(self.url).text
        self.id = re.search("release&id=(.*)&l=", page).group(1)

    def __set_start_end_page(self):
        self.start_page = int(self.start_episode / 30) + 1
        self.end_page = int(self.end_episode / 30) + 1

    def __get_page_data(self, page_url):
        return self.session.get(page_url).json()

    def __collect_episodes(self):
        printer("INFO", "Collecting episodes...", self.gui)

        page_count = self.start_page
        while page_count <= self.end_page:
            api_url = "https://animepahe.com/api?m=release&id=" + self.id + "&sort=episode_asc&page=" + str(page_count)
            api_data = self.__get_page_data(api_url)["data"]

            for data in api_data:
                epi_no = data["episode"]
                if epi_no < self.start_episode or epi_no > self.end_episode:
                    continue

                is_canon = data["filler"] == 0

                # AnimePahe is not having valid fillers list (always 0). Added for the completion
                if not self.is_filler and not is_canon:
                    print("Episode", str(epi_no), "is filler.. skipping...")
                    continue

                episode = Episode("Episode - " + str(epi_no), "Episode - " + str(epi_no))
                episode.id = data["session"]
                self.episodes.append(episode)

            page_count += 1

    def __set_kwik_links(self):
        printer("INFO", "Collecting kwik links...", self.gui)

        api_url = "https://animepahe.com/api?m=embed&p=kwik&id="
        for episode in self.episodes:
            temp_url = api_url + self.id + "&session=" + episode.id
            # print(temp_url)
            api_data = self.__get_page_data(temp_url)["data"]

            links = list(api_data.keys())

            # 720p
            link = api_data[links[0]]["720"]["url"]
            id = link.split("/")[-1]

            try:
                # 1080p
                if self.resolution == "1080":
                    link = api_data[links[1]]["1080"]["url"]
                    id = link.split("/")[-1]
            except Exception as ex:
                printer("ERROR", "1080p not available!", self.gui)
                printer("INFO", "Continuing with 720p link...", self.gui)

            episode.id = id
            page_url = "https://kwik.cx/f/" + id
            episode.page_url = page_url

            if not self.extractor.set_direct_link(episode):  # try setting at retrieval
                printer("INFO", "Second download link retrieval attempt", self.gui)
                if not self.extractor.set_direct_link(episode):
                    printer("INFO", "Third download link retrieval attempt", self.gui)
                    if not self.extractor.set_direct_link(episode):
                        printer("ERROR", "Failed all attempts to retrieve download link for " + episode.title, self.gui)

    def get_direct_links(self):
        try:
            self.__collect_episodes()
            self.__set_kwik_links()

            return self.episodes
        except Exception as ex:
            printer("ERROR", ex, self.gui)
            return None

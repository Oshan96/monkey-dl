import re
from functools import reduce

from bs4 import BeautifulSoup
from extractors.kwik_extractor import KwikExtractor
from scrapers.base_scraper import BaseScraper
from util.Color import printer
from util.Episode import Episode


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

    def __set_kwik_links(self, *, max_tries=3):
        printer("INFO", "Collecting kwik links...", self.gui)
        BASE_API_URL = "https://animepahe.com/api?m=embed&p=kwik&id={}&session={}"        
        
        for episode in self.episodes:
            available_urls = self.__get_page_data(BASE_API_URL.format(self.id, episode.id)).get('data', [])
            if not available_urls:
                printer("ERROR", "API error, AnimePahe API failed to retrieve available qualities.", self.gui)
                continue
            
            quality_dict = reduce(lambda d1, d2: d1 | d2, available_urls) # type: dict
            
            if not self.resolution in quality_dict:
                printer("ERROR", "Could not find the requested quality %sp, falling back to the first available quality." % self.resolution, self.gui)
                self.resolution = [*quality_dict.keys()][0] # Due to line 78, there is always a value here & an error occurence is impossible.
                
            printer("INFO", "Fetching stream url based on selected quality - %sp." % self.resolution, self.gui)
            
            episode.page_url = quality_dict.get(self.resolution, {}).get('kwik', "").replace('\\', '')
            episode.id = episode.page_url.split('/')[-1]
            
            tries = 1            
            success = False
            
            while tries <= max_tries and not success:
                if not self.extractor.set_direct_link(episode):
                    printer("INFO", "Failed to retrieve download link from URL for %s, try %d (max tries: %d)." % (episode.title, tries, max_tries), self.gui)
                else:
                    success = True
                tries += 1
            
            if not success:
                printer("ERROR", "Could not retrieve the download url for %s. (Possibly due to an extraction error)" % (episode.title), self.gui)    
            
    def get_direct_links(self):
        try:
            self.__collect_episodes()
            self.__set_kwik_links()

            return self.episodes
        except Exception as ex:
            printer("ERROR", ex, self.gui)
            return None
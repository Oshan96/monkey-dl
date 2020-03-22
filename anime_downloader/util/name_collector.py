import requests
from bs4 import BeautifulSoup
from util.Episode import Episode


class EpisodeNamesCollector:
    def __init__(self, url, start_episode, end_episode, is_filler=False, episodes=None):
        self.url = url
        self.start_episode = start_episode
        self.end_episode = end_episode
        self.is_filler = is_filler
        self.episodes = episodes

    def __extract_episode_names(self):
        episodes = []

        page = requests.get(self.url).content
        soup_html = BeautifulSoup(page, "html.parser")

        table = soup_html.find("table", attrs={"class": "EpisodeList"}).find("tbody")

        if self.is_filler:
            epis = table.findAll("tr")
        else:
            epis = table.findAll("tr", attrs={"class": ["anime_canon", "mixed_canon/filler", "manga_canon"]})

        for epi in epis:
            epi_no = int(epi.find("td", attrs={"class": "Number"}).text)

            if epi_no < self.start_episode or epi_no > self.end_episode:
                continue

            title = epi.find("td", attrs={"class": "Title"}).find("a").text
            episode = Episode(title, "Episode - " + str(epi_no))

            episodes.append(episode)

        return episodes

    def __get_episode(self, epis, episode):
        for epi in epis:
            if epi.episode == episode.episode:
                return epi

        return None

    def __set_episode_names(self, epis):
        fillers = []
        for episode in self.episodes:
            epi = self.__get_episode(epis, episode)
            if epi:
                episode.title = epi.title
                # print(episode.episode,"Title -",episode.title)
                epis.remove(epi)
            else:
                print(episode.episode,"is Filler, skipped")
                fillers.append(episode)

        return fillers

    def __remove_fillers(self, fillers):
        for filler in fillers:
            self.episodes.remove(filler)

    def collect_episode_names(self):
        epis = self.__extract_episode_names()

        if not self.episodes:
            return epis

        fillers = self.__set_episode_names(epis)

        if not self.is_filler:
            self.__remove_fillers(fillers)

        return self.episodes

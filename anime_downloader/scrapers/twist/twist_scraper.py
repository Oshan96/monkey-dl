import re
from scrapers.base_scraper import BaseScraper
from util.Color import printer
from util.Episode import Episode
from scrapers.twist.twist_source_decryptor import TwistSourceDecryptor


class TwistScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None):
        super().__init__(url, start_episode, end_episode, session, gui)

        url_data = re.search("(.*)/a/(.*)", self.url)
        print(url_data.group(2))
        self.anime_name = url_data.group(2).split("/")[0]
        self.twist_url_base = url_data.group(1)

        self.head = {"x-access-token": "1rj2vRtegS8Y60B3w3qNZm5T2Q0TN2NR"}

    def __get_source_data(self):
        sources_url = "{base_url}/api/anime/{anime_name}/sources".format(base_url=self.twist_url_base, anime_name=self.anime_name)
        return self.session.get(sources_url, headers=self.head).json()

    def __extract_download_urls(self):
        episodes = []
        epi_data = self.__get_source_data()
        for epi in epi_data:
            epi_no = epi["number"]

            if epi_no < self.start_episode or epi_no > self.end_episode:
                continue

            episode = Episode("Episode - " + str(epi_no), "Episode - " + str(epi_no))
            url = "https://twistcdn.bunny.sh" + TwistSourceDecryptor(epi["source"]).decrypt()

            episode.download_url = self.session.get(url, headers={"referer": self.twist_url_base}, allow_redirects=False).headers["location"]

            episode.request_headers = {"referer": "{base}/a/{name}/{id}".format(base=self.twist_url_base, name=self.anime_name, id=str(epi_no))}

            print(episode.download_url)

            episodes.append(episode)

        return episodes

    def get_direct_links(self):
        try:
            episodes = self.__extract_download_urls()
            if len(episodes) > 0:
                return episodes
            else:
                return None

        except Exception as ex:
            printer("ERROR", str(ex), self.gui)
            return None


# if __name__ == "__main__":
#     import cloudscraper as cs
#
#     for e in TwistScraper("https://twist.moe/a/one-piece/1", 900, 927, cs.create_scraper()).get_direct_links():
#         print(e.title, ":", e.download_url)

import re
from bs4 import BeautifulSoup
from util.Episode import Episode
from util.Color import printer
from scrapers.base_scraper import BaseScraper


class AnimeTakeScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, resolution="720"):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.domain_name = ".animetake.tv"
        self.resolution = resolution + "p"
        self.src_api_url = "https://vcdn.space/api/source/{id}"

    def __get_direct_link(self, epi_src_url):
        src_data = self.session.post(epi_src_url).json()
        sources = src_data["data"]

        link = None

        for source in sources:
            link = source["file"]
            try:
                head_data = self.session.get(link, allow_redirects=False)
                link = head_data.headers["location"]
            except Exception as ex:
                print(ex)

            if source["label"] == self.resolution:
                # print(link)
                # print("Desired resolution found")
                return link

        print("Desired resolution is not found, returning the first available resolution (or None if not found)")
        return link

    def __set_episode_direct_link(self, episode):
        page = self.session.get(episode.page_url).text
        # print(episode.page_url)
        vcdn_url = re.search(r'\"https://vcdn.space/v/(\S+)/\"', page) or re.search(r'\"https://vcdn.space/v/(\S+)\"', page)

        # print(vcdn_url.group(0))

        epi_id = vcdn_url.group(1)
        epi_sources_url = self.src_api_url.format(id=epi_id)

        try:
            link = self.__get_direct_link(epi_sources_url)
        except Exception:
            return False

        if link is not None:
            episode.download_url = link
            return True
        else:
            return False

    def extract_page_urls(self):
        printer("INFO", "Extracting page URLs...", self.gui)
        page = self.get_url_content().content
        # print(page)

        soup_html = BeautifulSoup(page, "html.parser")
        epis_container = soup_html.find(id="eps").find("div", attrs={"class": "list-group"})

        for anchor in epis_container.findAll("a", href=True):
            head = anchor.find("p", attrs={"class": "list-group-item-heading"}).text
            epi_no = int(re.search(r'(\d+)', head).group(1))

            if epi_no < self.start_episode or epi_no > self.end_episode:
                continue

            # print(epi_no)

            title = anchor.find("p", attrs={"class": "list-group-item-text"}).text.strip().split("\n")[0]
            page_url = "https://animetake.tv" + anchor["href"]

            episode = Episode(title, "Episode - " + str(epi_no))
            episode.page_url = page_url

            self.episodes.append(episode)

    def __set_download_links(self):
        printer("INFO", "Extracting download URLs...", self.gui)
        for episode in self.episodes:
            if not self.__set_episode_direct_link(episode):
                print("Failed to retrieve download link for {epi}".format(epi=episode.episode))

    def get_direct_links(self):
        self.extract_page_urls()
        if len(self.episodes) > 0:
            self.__set_download_links()

            return self.episodes

        else:
            return None

# if __name__ == "__main__":
#     import cloudscraper as cs
#     s = cs.create_scraper()
#
#     epis = AnimeTakeScraper("https://animetake.tv/anime/one-piece/",1,4,s).get_direct_links()
#
#     for epi in epis:
#         print(epi.episode)
#         print(epi.title)
#         print(epi.download_url)
#         print("-" * 25)
#         print()

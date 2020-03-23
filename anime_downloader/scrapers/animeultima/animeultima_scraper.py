import cloudscraper
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from util.Episode import Episode
from extractors.jwplayer_extractor import JWPlayerExtractor


class AnimeUltimaScraper(BaseScraper):

    def __init__(self, url, start_episode, end_episode, session, gui=None, is_dub=False, resolution="720"):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.is_dub = False
        self.resolution = resolution
        self.base_url = "https://www1.animeultima.to"
        self.extractor = JWPlayerExtractor(None, self.session)

    def get_anime_id(self):
        page = self.session.get(self.url).content
        soup_html = BeautifulSoup(page, "html.parser")

        # print(soup_html)

        button_with_id = soup_html.find("button", attrs={"class": "button"})

        if button_with_id:
            return button_with_id["data-id"]

        else:
            meta_tag = soup_html.find("meta", attrs={"property": "og:image"})
            if meta_tag:
                content_data = meta_tag["content"].split("/")
                return content_data[-2]

    def get_start_and_end_page(self, anime_id):
        start_page = 0
        end_page = 0

        data = self.session.get("https://www1.animeultima.to/api/episodeList?animeId=" + anime_id).json()

        last_page = data["last_page"]
        max_total_epis = last_page * 50

        if self.end_episode >= max_total_epis:
            start_page = 0
        elif (max_total_epis - self.end_episode) % 50 == 0:
            start_page = round((max_total_epis - self.end_episode) / 50) - 1
        else:
            start_page = round((max_total_epis - self.end_episode) / 50)

        if (max_total_epis - self.start_episode) % 50 == 0:
            end_page = round((max_total_epis - self.start_episode) / 50) - 1
        else:
            end_page = round((max_total_epis - self.start_episode) / 50)

        return start_page, end_page

    def get_page_url(self, url):
        page = self.session.get(url).content

        soup_html = BeautifulSoup(page, "html.parser")
        iframe = soup_html.find("iframe")

        if iframe:
            return self.base_url + iframe["src"]

        return None

    def collect_episodes(self, anime_id, start_page, end_page):
        base_url = "https://www1.animeultima.to/api/episodeList?animeId=" + anime_id + "&page="
        page_counter = start_page

        while page_counter <= end_page:
            url = base_url + str(page_counter)

            data = self.session.get(url).json()
            has_dub = data["anime"]["hasDub"]
            epis = data["episodes"]

            for epi in epis:
                epi_no = int(epi["episode_num"])

                if epi_no < self.start_episode or epi_no > self.end_episode:
                    continue

                title = epi["title"]
                page_url = None
                if not self.is_dub:
                    page_url = epi["urls"]["sub"]
                elif has_dub:
                    page_url = epi["urls"]["dub"]
                else:
                    print("Dubbed episodes not available")

                if page_url:
                    page_url = self.get_page_url(page_url)

                episode = Episode(title, "Episode - " + str(epi_no))
                episode.page_url = page_url
                episode.is_direct = False
                self.set_stream_url(episode)

                self.episodes.append(episode)

                print("Episode -", str(epi_no), "-", title)

            page_counter += 1

    def set_stream_url(self, episode):
        self.extractor.url = episode.page_url
        stream_url = self.extractor.extract_stream_link(self.resolution)
        print("Stream URL : " + stream_url)
        episode.download_url = stream_url

    def set_stream_urls(self):
        extractor = JWPlayerExtractor(None, self.session)
        for episode in self.episodes:
            extractor.url = episode.page_url
            stream_url = extractor.extract_stream_link(self.resolution)
            episode.dowload_url = stream_url

    # This will get called initially
    # Not fully implemented yet
    def get_direct_links(self):
        anime_id = self.get_anime_id()
        start_page, end_page = self.get_start_and_end_page(anime_id)

        print(anime_id)
        print(start_page, end_page)

        try:
            self.collect_episodes(anime_id, start_page, end_page)
            # sleep(2)
            # self.set_stream_urls()

            return self.episodes
        except Exception as ex:
            print(ex)
            return None


# if __name__ == "__main__":
#     session = cloudscraper.create_scraper()
    # id = get_anime_id("https://www1.animeultima.to/a/naruto-shippuuden_395410", session)
    # print(id)
    # print(get_start_and_end_page(session, id, 20, 450))

    # print(get_anime_id("https://www1.animeultima.to/a/naruto-shippuuden_395410", session))
    # print(get_start_and_end_page(1,513))
    # print(session.get("https://www1.animeultima.to/faststream/2336").text)
    # AnimeUltimaScraper("https://www1.animeultima.to/a/one-piece_708779", 261, 330, session).extract_episodes()
    epis = AnimeUltimaScraper("https://www1.animeultima.to/a/one-piece_708779", 261, 330, session).get_direct_links()

    for epi in epis:
        print(epi.episode, "-", epi.title)
        print(epi.is_direct)
        print(epi.download_url)
        print("-------------------------")

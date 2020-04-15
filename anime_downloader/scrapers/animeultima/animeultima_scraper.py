import re
import traceback
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from util.Episode import Episode
from extractors.jwplayer_extractor import JWPlayerExtractor
from util.js_unpacker import JsUnpacker


class AnimeUltimaScraper(BaseScraper):

    def __init__(self, url, start_episode, end_episode, session, gui=None, resolution="720", is_dub=False):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.is_dub = is_dub
        self.resolution = resolution
        self.base_url = "https://www1.animeultima.to"
        self.extractor = JWPlayerExtractor(None, None)

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

        return None

    def get_start_and_end_page(self, anime_id):
        # print("start end page")
        start_page = 0
        end_page = 0

        data = self.session.get("https://www1.animeultima.to/api/episodeList?animeId=" + anime_id).json()

        # print("start end data")
        # print(data)
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
        # print("get page url")
        page = self.session.get(url).content

        soup_html = BeautifulSoup(page, "html.parser")
        iframe = soup_html.find("iframe")

        if iframe:
            return self.base_url + iframe["src"]

        return None

    def set_stream_url(self, episode):
        # print("set stream")
        self.extractor.url = episode.page_url
        stream_url = self.extractor.extract_stream_link(self.resolution)
        print("Stream URL : " + stream_url)
        episode.download_url = stream_url

    def set_direct_url(self, episode, page_url):
        page = self.session.get(page_url).text
        func = re.search("eval\(.*\)", page).group(0)
        eval_data = JsUnpacker().eval(func)
        link = re.search('fone\s+=\s+\"(.*)\"', eval_data).group(1)
        # print(link)
        episode.download_url = link

    def collect_episodes(self, anime_id, start_page, end_page):
        # print("collect epis")
        base_url = "https://www1.animeultima.to/api/episodeList?animeId=" + anime_id + "&page="
        page_counter = start_page

        while page_counter <= end_page:
            url = base_url + str(page_counter)

            data = self.session.get(url).json()
            # print("data")
            # print(data)

            has_dub = data["anime"]["hasDub"]
            epis = data["episodes"]

            for epi in epis:
                epi_no = int(epi["episode_num"])
                # print(str(epi_no))

                if epi_no < self.start_episode or epi_no > self.end_episode:
                    continue

                title = epi["title"]
                page_url = None
                if not self.is_dub:
                    # print("sub")
                    page_url = epi["urls"]["sub"]
                elif has_dub:
                    page_url = epi["urls"]["dub"]
                else:
                    print("Dubbed episodes not available")

                if page_url is not None:
                    page_url = self.get_page_url(page_url)

                episode = Episode(title, "Episode - " + str(epi_no))
                episode.page_url = page_url
                # print(episode.page_url)
                if "animeultima.to/e/" not in page_url:
                    episode.is_direct = False
                    self.set_stream_url(episode)
                else:
                    print("Only direct url found, will use default resolution to download")
                    self.set_direct_url(episode, page_url)

                self.episodes.append(episode)

                print("Episode -", str(epi_no), "-", title)

            page_counter += 1

    def get_direct_links(self):
        # print("direct links")
        anime_id = self.get_anime_id()
        # print("anime id :", anime_id)
        if anime_id is None:
            anime_id = self.get_anime_id()
            if anime_id is None:
                anime_id = self.get_anime_id()

        try:
            # print(anime_id)
            start_page, end_page = self.get_start_and_end_page(anime_id)

            # print(start_page, end_page)
            self.collect_episodes(anime_id, start_page, end_page)

            return self.episodes
        except Exception as ex:
            trace = traceback.format_exc()
            print(trace)
            return None


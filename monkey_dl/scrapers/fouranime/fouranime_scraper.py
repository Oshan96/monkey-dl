import re
import traceback
from bs4 import BeautifulSoup
from util.Episode import Episode
from util import Color
from scrapers.base_scraper import BaseScraper
from util.js_unpacker import JsUnpacker


def get_packed(page):
    pack_links = [match.group(0) for match in re.finditer(r"eval\(.*\)", page)]
    return pack_links


class FourAnimeScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.domain_name = ".4anime.to"

    def __extract_page_urls(self):
        Color.printer("INFO", "Extracting page URLs...", self.gui)

        page = self.get_url_content().content

        soup_html = BeautifulSoup(page, "html.parser")
        # print(soup_html)

        try:
            server = soup_html.findAll("div", attrs={"class": "server"})[0]
            epi_ranges = server.findAll("ul", attrs={"class": "episodes"})

            for epi_range in epi_ranges:
                epi_tags = epi_range.findAll("a", href=True)

                for epi_tag in epi_tags:
                    epi_number = int(epi_tag.text)

                    if epi_number < self.start_episode or epi_number > self.end_episode:
                        continue

                    episode = Episode(str(epi_number), "Episode - " + str(epi_number))
                    episode.page_url = epi_tag["href"]

                    self.episodes.append(episode)

        except Exception as ex:
            trace = traceback.format_exc()
            print(trace)
            print(ex)
            return None

        return self.episodes

    def __extract_download_urls(self):
        Color.printer("INFO", "Extracting download URLs...", self.gui)
        success = True
        for episode in self.episodes:
            page = self.session.get(episode.page_url).content

            soup_html = BeautifulSoup(page, "html.parser")

            # print(soup_html)

            video_tag = soup_html.find("video", attrs={"id": "video1"})

            # print(video_tag)

            if video_tag is None:
                # print("checking div")
                video_tag = soup_html.find("div", attrs={"id": "video1"})
                # print(video_tag)

            if video_tag is None:
                # print("checking video")
                video_tag = soup_html.find("video")
                # print(video_tag)

            if video_tag is None or video_tag["src"] == '':
                print("checking for packed data")
                packed_funcs = get_packed(page.decode('utf-8'))
                # print(packed_funcs)

                if len(packed_funcs) > 0:
                    src = JsUnpacker().extract_link(packed_funcs[0])
                    if src is not None:
                        episode.download_url = src
                        success = True
                    else:
                        try:
                            src = JsUnpacker().extract_link(packed_funcs[1])
                            if src is not None:
                                episode.download_url = src
                                success = True
                                continue
                        except Exception:
                            Color.printer("ERROR", "Download link not found for " + episode.episode, self.gui)
                            success = False
                else:
                    Color.printer("ERROR", "Download link not found for " + episode.episode, self.gui)
                    success = False

                continue

            if video_tag is None:
                Color.printer("ERROR", "Download link not found for " + episode.episode, self.gui)
                success = False
                continue
            # print("----------------------------")
            try:
                episode.download_url = video_tag["src"]
                success = True
            except KeyError:
                # print(soup_html)
                Color.printer("ERROR", "Failed to retrieve download link not found for " + episode.episode, self.gui)
                continue

        return success

    def get_direct_links(self):
        if self.__extract_page_urls():
            if self.__extract_download_urls():
                return self.episodes

        return None
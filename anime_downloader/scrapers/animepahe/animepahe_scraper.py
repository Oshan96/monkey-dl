import re
import json
from bs4 import BeautifulSoup
from time import sleep
from util.Episode import Episode
from scrapers.base_scraper import BaseScraper
from util.Color import printer


class AnimePaheScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, resolution="720", is_filler=True):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.resolution = resolution
        self.is_filler = is_filler
        self.id = None
        self.base_url = "https://animepahe.com"
        self.start_page = 1
        self.end_page = 1

        self.__set_anime_id()
        self.__set_start_end_page()

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
                    link = api_data[links[0]]["1080"]["url"]
                    id = link.split("/")[-1]
            except Exception as ex:
                printer("ERROR", "1080p not available!", self.gui)
                printer("INFO", "Continuing with 720p link...", self.gui)

            episode.id = id
            page_url = "https://kwik.cx/f/" + id
            episode.page_url = page_url

            if not self.__set_direct_link(episode):  # try setting at retrieval
                printer("INFO", "Second download link retrieval attempt", self.gui)
                if not self.__set_direct_link(episode):
                    printer("INFO", "Third download link retrieval attempt", self.gui)
                    if not self.__set_direct_link(episode):
                        printer("ERROR", "Failed all attempts to retrieve download link for " + episode.title, self.gui)

    def __get_cookie_and_response(self, episode):
        printer("INFO", "Collecting request header values...", self.gui)

        head = {
            "referer": episode.page_url,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69"
        }
        response = self.session.get(episode.page_url, headers=head)
        cookie = []
        try:
            cookie.append(response.headers["set-cookie"])
            cookie.append(response)
        except Exception as ex:
            printer("ERROR", ex, self.gui)
            return None

        return cookie

    def __get_token(self, response):
        printer("INFO", "Collecting access token...", self.gui)
        page = response.text
        try:
            token = re.search("value\|(.*)\|([a-zA-Z])", page).group(1).split("|")[0]
            # print("TOKEN :", token)
            return token
        except Exception as ex:
            printer("ERROR", ex, self.gui)
            # print(page)
            return None

    def __set_direct_link(self, episode):
        cookie = self.__get_cookie_and_response(episode)
        if cookie is None:
            printer("INFO", "Retrying header retrieval...", self.gui)
            sleep(2)
            cookie = self.__get_cookie_and_response(episode)

        if cookie is None:
            printer("ERROR", "Couldn't find headers needed ...", self.gui)
            return False

        token = self.__get_token(cookie[1])

        if not token:
            printer("ERROR", "No token found... skipping", self.gui)
            return False

        head = {
            "origin": "https://kwik.cx",
            "referer": episode.page_url,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69",
            "cookie": cookie[0]
        }

        payload = {
            "_token": token
        }

        post_url = "https://kwik.cx/d/" + episode.id

        # print(head)

        resp_headers = self.session.post(post_url, data=payload, headers=head, allow_redirects=False).headers
        try:
            episode.download_url = resp_headers["location"]
        except Exception as ex:
            # print(resp_headers)
            # printer("ERROR", ex, self.gui)
            printer("ERROR", "Failed to retrieve direct url for " + episode.title, self.gui)
            return False

        return True

    # instead of calling this function in the end, direct links are retrieved for each episode one by one
    def __extract_direct_links(self):
        printer("INFO", "Collecting download links...", self.gui)

        for episode in self.episodes:
            cookie = self.__get_cookie_and_response(episode)
            if cookie is None:
                printer("INFO", "Retrying ...", self.gui)
                sleep(2)
                cookie = self.__get_cookie_and_response(episode)

            if cookie is None:
                printer("ERROR", "Skipping ...", self.gui)
                continue

            token = self.__get_token(cookie[1])

            if not token:
                printer("ERROR", "No token found... skipping", self.gui)
                continue

            head = {
                "origin": "https://kwik.cx",
                "referer": episode.page_url,
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69",
                "cookie": cookie[0]
            }

            payload = {
                "_token": token
            }

            post_url = "https://kwik.cx/d/" + episode.id

            print(head)

            resp_headers = self.session.post(post_url, data=payload, headers=head, allow_redirects=False).headers
            try:
                episode.download_url = resp_headers["location"]
            except Exception as ex:
                print(resp_headers)
                printer("ERROR", ex, self.gui)
                printer("ERROR", "Failed to retrieve direct url for " + episode.title, self.gui)
                continue

    def get_direct_links(self):
        try:
            self.__collect_episodes()
            self.__set_kwik_links()
            # sleep(3)
            # self.__extract_direct_links()

            return self.episodes
        except Exception as ex:
            printer("ERROR", ex, self.gui)
            return None


# if __name__ == "__main__":
#     import cloudscraper
#
#     session = cloudscraper.create_scraper()
#     scr = AnimePaheScraper("https://animepahe.com/anime/one-piece", 217, 223, session)
#     eps = scr.get_direct_links()
#
#     for ep in eps:
#         print(ep.title)
#         print(ep.download_url)
#         print("=============================\n")

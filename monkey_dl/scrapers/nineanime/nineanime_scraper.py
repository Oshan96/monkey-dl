import json
from bs4 import BeautifulSoup
from util import Color
from util.Episode import Episode
from util.captcha_solver import TwoCaptchaSolver
from scrapers.base_scraper import BaseScraper
from extractors.mp4upload_extractor import Mp4UploadExtractor


class NineAnimeScraper(BaseScraper):

    def __init__(self, url, start_episode, end_episode, session, gui=None, token=None):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.token = token
        self.api_key = None
        self.ts_no = None
        self.server_id = None
        self.site_key = "6LfEtpwUAAAAABoJ_595sf-Hh0psstoatwZpLex1"
        self.server_name = "Mp4upload"
        self.nine_anime_url = "https://9anime.to"

        self.headers = {"origin": self.nine_anime_url, "referer": url, "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36 Edg/80.0.361.109"}

        self.episodes_url = "https://9anime.to/ajax/film/servers/" + url.split(".")[2].split("/")[0]

        if not token:
            try:
                with open("settings.json") as (json_file):
                    data = json.load(json_file)
                    self.api_key = data["api_key"]
            except:
                Color.printer("ERROR", "Reading settings file failed! Continue without API key...", self.gui)
                self.api_key = ""

    def __get_mp4upload_index(self, servers_container):
        server_names = servers_container.findAll("span", attrs={"class": "tab"})

        for i in range(0, len(server_names)):
            if server_names[i].text.lower() == self.server_name.lower():
                self.server_id = server_names[i]["data-name"]
                return i

        return None

    def __verify(self):
        payload = {
            "g-recaptcha-response": self.token
        }

        data = self.session.post("https://9anime.to/waf-verify", data=payload, headers=self.headers, allow_redirects=False)
        self.headers["cookie"] = data.headers["set-cookie"]

    def __extract_page_urls(self):
        d = self.session.get("https://9anime.to/waf-verify", headers=self.headers, allow_redirects=True)
        self.headers["cookie"] = d.headers["set-cookie"]

        if self.token is None:
            if self.api_key != "" and self.api_key != "insert_2captcha_api_key":
                Color.printer("INFO", "Solving recaptcha...", self.gui)

                captcha_solver = TwoCaptchaSolver("https://9anime.to/waf-verify", self.site_key, self.api_key, self.session)

                self.token = captcha_solver.solve()
                if not self.token:
                    Color.printer("ERROR", "Captcha solving failed!", self.gui)
                    Color.printer("INFO", "Trying to continue ...", self.gui)

        if self.token:
            # print(self.token)
            self.__verify()
        else:
            Color.printer("INFO", "No API key or token given, trying to continue...", self.gui)

        Color.printer("INFO", "Extracting page URLs...", self.gui)

        data = self.session.get(self.url, headers=self.headers)
        anime_page = data.content

        soup_html = BeautifulSoup(anime_page, "html.parser")

        try:
            self.ts_no = soup_html.find("html")["data-ts"]

            eps_url = self.episodes_url + "?ts=" + self.ts_no

            self.headers["referer"] = eps_url

            resp = self.session.get(eps_url, headers=self.headers, allow_redirects=False)
            epi_data = resp.json()["html"]

            # print(epi_data)

            soup = BeautifulSoup(epi_data, "html.parser")

            servers_container = soup.find("span", attrs={"class": "tabs"})

            mp4upload_index = self.__get_mp4upload_index(servers_container)

            if mp4upload_index is None:
                return None

            mp4upload_server = soup.findAll("div", attrs={"class": "server"})[mp4upload_index]

            episode_ranges = mp4upload_server.findAll("ul", attrs={"class": "episodes"})

            for episode_range in episode_ranges:
                eps = episode_range.findAll("a", href=True)
                for episode in eps:
                    epi_number = int(episode.text)

                    if epi_number < self.start_episode or epi_number > self.end_episode:
                        continue

                    epi = Episode(str(epi_number), "Episode - " + str(epi_number))

                    epi.page_url = self.nine_anime_url + episode["href"]
                    epi.id = episode["data-id"]

                    self.episodes.append(epi)
        except Exception as ex:
            Color.printer("ERROR", ex, self.gui)
            return None

        return self.episodes

    def __extract_download_urls(self):
        down_base = "https://9anime.to/ajax/episode/info?"
        Color.printer("INFO", "Extracting download URLs...", self.gui)

        for episode in self.episodes:
            if (episode.id is None):
                episode.download_url = None
                continue

            url = down_base + "ts=" + self.ts_no + "&id=" + episode.id + "&server=" + self.server_id
            target = self.session.get(url, headers=self.headers).json()["target"]

            episode.page_url = target

            download_url = Mp4UploadExtractor(target, self.session).extract_direct_url()

            episode.download_url = download_url

    def get_direct_links(self):
        if self.__extract_page_urls():
            self.__extract_download_urls()

            return self.episodes

        return None

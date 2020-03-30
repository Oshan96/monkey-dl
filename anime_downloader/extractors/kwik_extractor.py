import re
from util.Color import printer
from time import sleep
from extractors.kwik_token_extractor import kwik_token_extractor
from bs4 import BeautifulSoup


class KwikExtractor:
    def __init__(self, session, gui=None):
        self.session = session
        self.gui = gui
        self.token = None

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

    def __set_token(self, response_text):
        data = re.search("[\S]+\",[\d]+,\"[\S]+\",[\d]+,[\d]+,[\d]+", response_text).group(0)
        parameters = data.split(",")
        para1 = parameters[0].strip("\"")
        para2 = int(parameters[1])
        para3 = parameters[2].strip("\"")
        para4 = int(parameters[3])
        para5 = int(parameters[4])
        para6 = int(parameters[5])

        page_data = kwik_token_extractor.extract_data(para1, para2, para3, para4, para5, para6)
        page_data = BeautifulSoup(page_data, "html.parser")

        input_field = page_data.find("input", attrs={"name": "_token"})

        # print(input_field)

        if input_field is not None:
            self.token = input_field["value"]
            # print(self.token)
            return True

        return False

    def set_direct_link(self, episode):
        cookie = self.__get_cookie_and_response(episode)
        if cookie is None:
            printer("INFO", "Retrying header retrieval...", self.gui)
            sleep(2)
            cookie = self.__get_cookie_and_response(episode)

        if cookie is None:
            printer("ERROR", "Couldn't find headers needed ...", self.gui)
            return False

        # token = self.__get_token(cookie[1])

        if self.token is None:
            self.__set_token(cookie[1].text)

            if self.token is None:
                printer("ERROR", "No token found... skipping", self.gui)
                return False

        # print(cookie[0])
        head = {
            "origin": "https://kwik.cx",
            "referer": episode.page_url,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36 Edg/80.0.361.69",
            "cookie": cookie[0]
        }

        payload = {
            "_token": self.token
        }

        post_url = "https://kwik.cx/d/" + episode.id

        # print(head)
        # print(payload)
        # print(post_url)

        resp_headers = self.session.post(post_url, data=payload, headers=head, allow_redirects=False)
        # print(resp_headers)
        try:
            episode.download_url = resp_headers.headers["location"]
            # print(resp_headers.headers["location"])
        except Exception as ex:
            # print(resp_headers)
            # printer("ERROR", ex, self.gui)
            self.token = None
            printer("ERROR", "Failed to retrieve direct url for " + episode.title, self.gui)
            return False

        return True

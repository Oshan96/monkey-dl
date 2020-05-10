import requests
import browser_cookie3 as bc
from cloudscraper.exceptions import CloudflareException
from util.Color import printer


class BaseScraper:
    def __init__(self, url, start_episode, end_episode, session, gui=None):
        self.url = url
        if not self.url.endswith("/"):
            self.url += "/"
        self.start_episode = start_episode
        self.end_episode = end_episode
        self.session = session
        self.gui = gui
        self.domain_name = None
        self.host = None

        self.episodes = []

    def get_url_content(self):
        try:
            page = self.session.get(self.url)
            return page
        except CloudflareException:
            print(
                "Cloudflare exception raised! browser cookies will be used in retry. Make sure you visited the given url from chrome/firefox")
            printer("ERROR", "Cloudflare exception raised!", self.gui)
            printer("INFO",
                    "browser cookies will be used in retry. Make sure you visited the given url from chrome/firefox browser.",
                    self.gui)

            self.session = requests.Session()

            return self.request_from_cookies(session=self.session)

    def request_from_cookies(self, url=None, session=None, domain_name=None, referer=None):
        if url is None:
            url = self.url

        if session is None:
            session = self.session

        if domain_name is None:
            domain_name = self.domain_name

        if referer is None:
            referer = url

        # print(self.domain_name)
        cookies = bc.load(domain_name=domain_name)
        # session = requests.Session()

        d = {}
        for c in cookies:
            d[c.name] = c.value
        # print(d)

        c_head = ""
        for key, value in d.items():
            c_head += "{k}={v}; ".format(k=key, v=value)

        c_head = c_head.strip()
        if c_head != "":
            c_head = c_head[:-1]

        head = {
            "cookie": c_head,
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
            "referer": referer
        }

        # print(head)

        session.cookies.update(cookies)
        session.headers.update(head)

        if self.host is not None:
            session.headers.update({"Host": self.host})

        # print(session.headers)
        # print(url)
        # print(self.session.get(self.url))

        page = session.get(url)

        return page

    def get_direct_links(self):
        raise NotImplementedError

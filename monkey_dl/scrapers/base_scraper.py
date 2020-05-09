import re
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

        self.episodes = []

    def get_url_content(self):
        try:
            page = self.session.get(self.url).content
            return page
        except CloudflareException:
            print(
                "Cloudflare exception raised! browser cookies will be used in retry. Make sure you visited the given url from chrome/firefox")
            printer("ERROR", "Cloudflare exception raised!", self.gui)
            printer("INFO",
                    "browser cookies will be used in retry. Make sure you visited the given url from chrome/firefox browser.",
                    self.gui)

            return self.request_from_cookies()

    def request_from_cookies(self):
        print(self.domain_name)
        cookies = bc.load(domain_name=self.domain_name)
        self.session = requests.Session()

        host_re = re.search(r'[htps]+://(\S+)/\S+', self.url) or re.search(r'[htps]+://(\S+)', self.url)
        host = host_re.group(1).split("/")[0]
        # print(host)

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
            "referer": self.url
        }

        # print(head)

        self.session.cookies.update(cookies)
        self.session.headers.update(head)
        # print(self.session.headers)
        # print(self.url)
        # print(self.session.get(self.url))

        page = self.session.get(self.url).text

        return page

    def get_direct_links(self):
        raise NotImplementedError

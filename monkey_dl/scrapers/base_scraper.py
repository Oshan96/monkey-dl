import requests
import browser_cookie3 as bc
from cloudscraper.exceptions import CloudflareException
from util.Color import printer


class BaseScraper:
    def __init__(self, url, start_episode, end_episode, session, gui=None):
        self.url = url
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

            cookies = bc.load(domain_name=self.domain_name)
            self.session = requests.Session()

            d = {}
            for c in cookies:
                d[c.name] = c.value
            # print(d)

            cookie_header = "__cfduid={uid}; cf_clearance={clear}"

            c_head = cookie_header.format(uid=d['__cfduid'], clear=d['cf_clearance'])

            if self.domain_name == ".animeultima.to":
                c_head += "; XSRF-TOKEN={xsrf}".format(xsrf=d["XSRF-TOKEN"])

            head = {"cookie": c_head,
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
                    "referer": self.url
                    }

            self.session.cookies.update(cookies)
            self.session.headers.update(head)

            page = self.session.get(self.url).text

            return page

    def get_direct_links(self):
        raise NotImplementedError

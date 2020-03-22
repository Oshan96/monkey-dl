from bs4 import BeautifulSoup
from util import Color
from util.Episode import Episode
from scrapers.base_scraper import BaseScraper


class AnimePaheScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None):
        super().__init__(url, start_episode, end_episode, session, gui)

    def get_direct_links(self):
        pass

import re
from bs4 import BeautifulSoup
from util.Episode import Episode
from scrapers.base_scraper import BaseScraper
from util.Color import printer
import requests


class ShiroScraper(BaseScraper):
    def __init__(self, url, start_episode, end_episode, session, gui=None, is_dub=False):
        super().__init__(url, start_episode, end_episode, session, gui)
        self.token = self.get_token()

    def get_token(self):
        r = requests.get('https://shiro.is').text
        script = 'https://shiro.is' + re.search(r'src\=\"(\/static\/js\/main\..*?)\"', r)[1]  # noqa
        script = requests.get(script).text
        token = re.search(r'token\:\"(.*?)\"', script)[1]
        return token

    def __collect_episodes(self):
        printer("INFO", "Extracting page URLs...", self.gui)
        slug = self.url.split('/')[-1]
        if slug == '':
            slug = self.url[:-1].split('/')[-1]
        if 'episode' in slug:
            api_link = 'https://ani.api-web.site/anime-episode/slug/' + slug
            r = requests.get(api_link, params={'token': self.token}).json()
            slug = r['data']['anime_slug']
        api_link = 'https://ani.api-web.site/anime/slug/' + slug
        r = requests.get(api_link, params={'token': self.token}).json()
        if r['status'] == 'Found':
            episodes = [
                [x['name'], 'https://ani.googledrive.stream/vidstreaming/vid-ad/' + x['videos'][0]['video_id'], x['episode_number']]  # noqa
                for x in r['data']['episodes']
            ]
        else:
            episodes = []
        super_eps = []
        for episode in episodes:
            if episode[2] < self.start_episode or episode[2] > self.end_episode:  # noqa
                continue

            ep = Episode(episode[0], f'Episode - {episode[2]}')
            try:
                ep.download_url = re.search(r'\"file\"\:\"(.*?)\"', requests.get(episode[1]).text)[1]  # noqa
            except Exception:
                printer("ERROR", "Couldn't get a download link for episode: {}".format(episode[0]), self.gui)
                continue
            super_eps.append(ep)
        return super_eps

    def get_direct_links(self):
        try:
            episodes = self.__collect_episodes()
            if len(episodes) > 0:
                return episodes
            else:
                return None

        except Exception as ex:
            printer("ERROR", str(ex), self.gui)
            return None

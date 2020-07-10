import shutil
import ssl
import traceback
import requests
from platform import system
from queue import Queue
from threading import Thread
from util import Color
from util.hls_downloader import HLSDownloader

from util.Color import printer
from time import sleep
import cloudscraper
from scrapers.fouranime.fouranime_scraper import FourAnimeScraper
from scrapers.nineanime.nineanime_scraper import NineAnimeScraper
from scrapers.animeultima.animeultima_scraper import AnimeUltimaScraper
from scrapers.animeflix.animeflix_scraper import AnimeFlixScraper
from scrapers.animepahe.animepahe_scraper import AnimePaheScraper
from scrapers.gogoanime.gogoanime_scraper import GoGoAnimeScraper
from scrapers.animefreak.animefreak_scraper import AnimeFreakScraper
from scrapers.animetake.animetake_scraper import AnimeTakeScraper
from scrapers.twist.twist_scraper import TwistScraper

def clean_file_name(file_name):
    for c in r'[]/\;,><&*:%=+@#^()|?^':
        file_name = file_name.replace(c, '')

    return file_name


class Worker(Thread):
    def __init__(self, tasks, gui=None):
        Thread.__init__(self)
        self.tasks = tasks
        self.gui = gui
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, arg, kargs = self.tasks.get()
            try:
                func(*arg, **kargs)
            except Exception as ex:
                Color.printer("ERROR", ex, self.gui)
            finally:
                self.tasks.task_done()


class ThreadPool:
    def __init__(self, num_threads, gui=None):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks, gui)

    def add_task(self, func, *arg, **kargs):
        self.tasks.put((func, arg, kargs))

    def map(self, func, args_list):
        for arg in args_list:
            self.add_task(func, arg)

    def wait_completion(self):
        self.tasks.join()


class Downloader:
    def __init__(self, anime_url, names_url, start_epi, end_epi, is_filler, is_titles, token, threads=1, directory=".", gui=None, resolution="720", is_dub=False):
        self.anime_url = anime_url
        self.names_url = names_url
        self.start_epi = start_epi
        self.end_epi   = end_epi
        self.is_filler = is_filler
        self.is_titles = is_titles
        self.token = token
        self.resolution = resolution
        self.is_dub = is_dub

        self.directory = directory
        self.threads = threads
        #self.episodes = episodes
        #self.is_titles = is_titles
        self.gui = gui

        self.episodes = None

    def __download_episode(self, episode):
        if system() == "Windows":
            episode.title = clean_file_name(episode.title)

        if episode.is_direct:
            if episode.download_url is None:
                Color.printer("ERROR", "Download URL is not set for " + episode.episode + ", skipping...", self.gui)
                return

            Color.printer("INFO", "Downloading " + episode.episode + "...", self.gui)

            # print(self.is_titles)
            # print(episode.title)

            if self.is_titles:
                # print("with title")
                file_name = self.directory + episode.episode + " - " + episode.title + ".mp4"
            else:
                # print("without title")
                file_name = self.directory + episode.episode + ".mp4"

            with requests.get(episode.download_url, headers=episode.request_headers, stream=True) as r:
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(r.raw, f, length=16 * 1024 * 1024)

            Color.printer("INFO", episode.episode + " finished downloading...", self.gui)

        else:
            Color.printer("INFO", "HLS link found. Using custom HLSDownloader to download...", self.gui)
            try:
                HLSDownloader(episode, self.directory, requests.session(), self.gui).download()
            except Exception:
                trace = traceback.format_exc()
                print(trace)
                Color.printer("ERROR", "Custom HLS Downloader failed to download {epi}".format(epi=episode.episode),
                              self.gui)

    def get_episodes(self):
        max_val = 100

        session = cloudscraper.create_scraper()
        api_key = ""
        try:
            with open("settings.json", "r") as json_file:
                data = json.load(json_file)
                api_key = data["api_key"]
        except Exception:
            api_key = ""

        if api_key != "" and api_key != "insert_2captcha_api_key":
            session = cloudscraper.create_scraper(
                    recaptcha={
                        'provider': '2captcha',
                        'api_key': api_key
                        }
                    )

        scraper = None
        self.episodes = []

        anime_url = self.anime_url.lower()
        start_epi = self.start_epi
        end_epi = self.end_epi
        gui = self.gui
        token = self.gui
        resolution = self.resolution
        is_dub = self.is_dub
        is_filler = self.is_filler

        try:
            if "9anime" in anime_url:
                printer("INFO", "9Anime URL detected...", gui)
                scraper = NineAnimeScraper(anime_url, start_epi, end_epi, session, gui, token)

            elif "4anime.to" in anime_url:
                printer("INFO", "4Anime URL detected...", gui)
                scraper = FourAnimeScraper(anime_url, start_epi, end_epi, session, gui)

            elif "animeultima.to" in anime_url:
                printer("INFO", "AnimeUltima URL detected...", gui)
                scraper = AnimeUltimaScraper(anime_url, start_epi, end_epi, session, gui, resolution, is_dub)

            elif "animeflix" in anime_url:
                printer("INFO", "AnimeFlix URL detected...", gui)
                scraper = AnimeFlixScraper(anime_url, start_epi, end_epi, session, gui, resolution, is_dub)

            elif "gogoanime" in anime_url:
                printer("INFO", "GoGoAnime URL detected...", gui)
                if "gogoanime.pro" in anime_url:
                    printer("ERROR", "goganime.pro links are not supported yet try gogoanime.io or gogoanime.video", gui)
                    return

                scraper = GoGoAnimeScraper(anime_url, start_epi, end_epi, session, gui, resolution)

            elif "animefreak" in anime_url:
                printer("INFO", "AnimeFreak URL detected...", gui)
                scraper = AnimeFreakScraper(anime_url, start_epi, end_epi, session, gui, is_dub)

            elif "twist" in anime_url:
                printer("INFO", "Twist URL detected...", gui)
                scraper = TwistScraper(anime_url, start_epi, end_epi, session, gui)

            elif "animetake" in anime_url:
                printer("INFO", "AnimeTake URL detected...", gui)
                scraper = AnimeTakeScraper(anime_url, start_epi, end_epi, session, gui, resolution)

            elif "animepahe.com" in anime_url:
                printer("INFO", "AnimePahe URL detected...", gui)

                if api_key == "" or api_key == "insert_2captcha_api_key":
                    printer("ERROR", "You need 2captcha API key to download from AnimePahe!", gui)
                    printer("ERROR", "Set 2captcha API key in 'settings.json' file to download from AnimePahe!", gui)
                    return

                scraper = AnimePaheScraper(anime_url, start_epi, end_epi, session, gui, resolution, is_filler)

            else:
                printer("ERROR", "Incorrect URL provided!", gui)
                return

            printer("INFO", "Collecting download links...", gui)
            self.episodes = scraper.get_direct_links()

            if self.episodes is None:
                printer("INFO", "Retrying to collect download links...", gui)
                sleep(5)
                self.episodes = scraper.get_direct_links()

            if self.episodes:
                if self.is_titles:
                    printer("INFO", "Setting episode titles...", gui)
                    self.episodes = EpisodeNamesCollector(names_url, start_epi, end_epi, is_filler,
                            self.episodes).collect_episode_names()

            else:
                printer("ERROR", "Failed to retrieve download links!", gui)
                return

            max_val = len(self.episodes)

        except Exception as ex:
            trace = traceback.format_exc()
            print(trace)
            printer("ERROR", ex, gui)
            printer("ERROR", "Something went wrong! Please close and restart Anime Downloader to retry!", gui)

        return max_val


    def download(self):
        if self.episodes is None:
            self.get_episodes()

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        Color.printer("INFO", "Downloading started...", self.gui)

        pool = ThreadPool(self.threads, self.gui)

        pool.map(self.__download_episode, self.episodes)
        pool.wait_completion()

        Color.printer("INFO", "Downloading finished!", self.gui)

import warnings
import ssl
import argparse
import requests
import shutil
import os
import sys
import traceback
from platform import system
from threading import Thread
from queue import Queue
from art import text2art
from util import Color
from util.ffmpeg_downloader import FFMPEGDownloader
from util.hls_downloader import HLSDownloader
from scrapers.nineanime import Anime_Scraper

directory = ""
threads = 1
token = None
titles = False
args = None
gui = None


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
    def __init__(self, directory, episodes, threads=1, gui=None, is_titles=False):
        self.directory = directory
        self.threads = threads
        self.episodes = episodes
        self.is_titles = is_titles
        self.gui = gui

    def __clean_file_name(self, file_name):
        for c in r'[]/\;,><&*:%=+@#^()|?^':
            file_name = file_name.replace(c, '')

        return file_name

    def __download_episode(self, episode):
        if system() == "Windows":
            episode.title = self.__clean_file_name(episode.title)

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

            with requests.get(episode.download_url, headers=episode.request_headers, stream=True, verify=False) as r:
                with open(file_name, 'wb') as f:
                    shutil.copyfileobj(r.raw, f, length=16 * 1024 * 1024)

            Color.printer("INFO", episode.episode + " finished downloading...", self.gui)

        else:
            Color.printer("INFO", "HLS link found. Using custom HLSDownloader to download...", self.gui)
            try:
                HLSDownloader(episode, self.directory, requests.session(), self.gui).download()
            except Exception as ex:
                trace = traceback.format_exc()
                print(trace)
                Color.printer("ERROR", "Custom HLS Downloader failed! Using FFMPEG to download...", self.gui)
                FFMPEGDownloader(episode, self.directory, self.gui).download()

    def download(self):

        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            # Legacy Python that doesn't verify HTTPS certificates by default
            pass
        else:
            # Handle target environment that doesn't support HTTPS verification
            ssl._create_default_https_context = _create_unverified_https_context

        Color.printer("INFO", "Downloading started...", self.gui)

        pool = ThreadPool(self.threads, gui)

        pool.map(self.__download_episode, self.episodes)
        pool.wait_completion()

        Color.printer("INFO", "Downloading finished!", self.gui)


def print_banner():
    banner = text2art("Anime    Downloader")
    Color.printer("BANNER", banner)


def main():
    global directory, args, threads, titles, token

    print_banner()

    parser = argparse.ArgumentParser(description="Anime Downloader Command Line Tool")
    argparse.ArgumentParser(description="Help option parcer for Anime Downloader Command Line Tool", add_help=False,
                            formatter_class=argparse.HelpFormatter)

    parser.add_argument("-u", "--url", required=True, help="9Anime.to URL for the anime to be downloaded", dest="url")
    parser.add_argument("-n", "--names", required=True,
                        help="https://www.animefillerlist.com/ URL to retrieve episode titles", dest="title_url")
    parser.add_argument("-d", "--directory", required=False,
                        help="Download destination. Will use the current directory if not provided", default="",
                        dest="dir")
    parser.add_argument("-s", "--start", required=False, help="Starting episode", default=1, type=int, dest="start")
    parser.add_argument("-e", "--end", required=False, help="End episode", default=9999, type=int, dest="end")
    parser.add_argument("-c", "--code", required=False,
                        help="Recaptcha answer token code. Insert this if you don't have 2captcha captcha bypass api_key",
                        default=None, dest="token")
    parser.add_argument("-t", "--threads", required=False,
                        help="Number of parrallel downloads. Will download sequencially if not provided", default=1,
                        type=int, dest="threads")
    parser.add_argument("-f", "--filler", required=False, help="Whether fillers needed", default=True, type=bool,
                        dest="isFiller")

    args = parser.parse_args()

    Anime_Scraper.download_9anime_url = args.url
    Anime_Scraper.title_url = args.title_url
    Anime_Scraper.isFiller = args.isFiller

    token = args.token
    directory = args.dir
    threads = args.threads

    if args.title_url:
        titles = True

    if directory != "":
        directory = directory.replace("\\", "/")
        if not directory.endswith("/"):
            directory += "/"

    Anime_Scraper.main(args.start, args.end, token)

    Downloader(directory, Anime_Scraper.episodes, threads, gui, titles).download()


if __name__ == "__main__":
    # suppress warnings
    warnings.filterwarnings("ignore")

    # activate color codes
    if sys.platform.lower() == "win32":
        os.system("color")

    main()

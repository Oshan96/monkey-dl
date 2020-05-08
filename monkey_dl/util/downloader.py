import shutil
import ssl
import traceback
import requests
from platform import system
from queue import Queue
from threading import Thread
from util import Color
from util.hls_downloader import HLSDownloader


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
    def __init__(self, directory, episodes, threads=1, gui=None, is_titles=False):
        self.directory = directory
        self.threads = threads
        self.episodes = episodes
        self.is_titles = is_titles
        self.gui = gui

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

        pool = ThreadPool(self.threads, self.gui)

        pool.map(self.__download_episode, self.episodes)
        pool.wait_completion()

        Color.printer("INFO", "Downloading finished!", self.gui)

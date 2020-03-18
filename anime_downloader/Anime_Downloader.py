from scrapers.nineanime import Anime_Scraper
from util import Color
import warnings
import ssl
import argparse
import requests
import shutil
import os
import sys
from platform import system

from threading import Thread
from queue import Queue
from art import text2art

directory = ""
threads = 1

token = None

titles = False

args = None

gui = None

class Worker(Thread) :
    def __init__(self, tasks) :
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()
    
    def run(self) :
        global gui
        while True :
            func, arg, kargs = self.tasks.get()
            try :
                func(*arg, **kargs)
            except Exception as ex :
                # print(ex)
                Color.printer("ERROR", ex, gui)
            finally :
                self.tasks.task_done()

class ThreadPool :
    def __init__(self, num_threads) :
        self.tasks = Queue(num_threads)
        for _ in range(num_threads) :
            Worker(self.tasks)
    
    def add_task(self, func, *arg, **kargs) :
        self.tasks.put((func, arg, kargs))
    
    def map(self, func, args_list) :
        for arg in args_list :
            self.add_task(func, arg)
    
    def wait_completion(self) :
        self.tasks.join()


def clean_file_name(file_name) :
    for c in r'[]/\;,><&*:%=+@#^()|?^':
        file_name = file_name.replace(c,'')
    
    return file_name

def download_episode(episode) :
    global titles, gui

    Color.printer("INFO", "Downloading " + episode.episode + "...", gui)

    if system() == "Windows" :
        episode.title = clean_file_name(episode.title)

    if titles :
        file_name = directory + episode.episode + " - " + episode.title + ".mp4"
    else :
        file_name = directory+episode.episode+".mp4"

    with requests.get(episode.download_url, stream=True, verify=False) as r:
        with open(file_name, 'wb') as f:
            shutil.copyfileobj(r.raw, f, length=16*1024*1024)

    Color.printer("INFO", episode.episode + " finished downloading...", gui)


def download() :
    global directory, threads, gui

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        # Legacy Python that doesn't verify HTTPS certificates by default
        pass
    else:
        # Handle target environment that doesn't support HTTPS verification
        ssl._create_default_https_context = _create_unverified_https_context

    Color.printer("INFO", "Downloading started...", gui)

    # for episode in Anime_Scraper.episodes :
    #     print("Downloading", episode.episode)
    #     urllib.request.urlretrieve(episode.download_url, directory+episode.episode+".mp4")
    
    pool = ThreadPool(threads)

    pool.map(download_episode, Anime_Scraper.episodes)
    pool.wait_completion()

    Color.printer("INFO", "Downloading finished!", gui)


def print_banner() :
    banner = text2art("Anime    Downloader")
    Color.printer("BANNER", banner)


def main() :
    global directory, args, threads, titles, token

    print_banner()

    parser = argparse.ArgumentParser(description="Anime Downloader Command Line Tool")
    argparse.ArgumentParser(description="Help option parcer for Anime Downloader Command Line Tool", add_help=False, formatter_class=argparse.HelpFormatter)

    parser.add_argument("-u", "--url", required=True, help="9Anime.to URL for the anime to be downloaded", dest="url")
    parser.add_argument("-n", "--names", required=True, help="https://www.animefillerlist.com/ URL to retrieve episode titles", dest="title_url")
    parser.add_argument("-d", "--directory", required=False, help="Download destination. Will use the current directory if not provided", default="" , dest="dir")
    parser.add_argument("-s", "--start", required=False, help="Starting episode",default=1, type=int , dest="start")
    parser.add_argument("-e", "--end", required=False, help="End episode", default=9999, type=int ,dest="end")
    parser.add_argument("-c", "--code", required=False, help="Recaptcha answer token code. Insert this if you don't have 2captcha captcha bypass api_key", default=None, dest="token")
    parser.add_argument("-t", "--threads", required=False, help="Number of parrallel downloads. Will download sequencially if not provided", default=1, type=int ,dest="threads")
    parser.add_argument("-f", "--filler", required=False, help="Whether fillers needed", default=True, type=bool ,dest="isFiller")

    args = parser.parse_args()

    Anime_Scraper.download_9anime_url = args.url
    Anime_Scraper.title_url = args.title_url
    Anime_Scraper.isFiller = args.isFiller
    # Anime_Scraper.ts_no = args.ts_no
    token = args.token
    directory = args.dir
    threads = args.threads

    if args.title_url :
        titles = True

    if directory != "" :
        directory = directory.replace("\\", "/")
        if not directory.endswith("/") :
            directory+="/"
    
    Anime_Scraper.main(args.start, args.end, token)

    download()

if __name__ == "__main__":
    #suppress warnings
    warnings.filterwarnings("ignore")
    
    #activate color codes
    if sys.platform.lower() == "win32" :
        os.system("color")  
    
    main()

from queue import Queue
from gui.GUI import AnimeGUI

import argparse
from util.downloader import Downloader

def download(anime_url, names_url, start_epi, end_epi, is_filler, is_titles, token, threads, directory, gui,
             resolution="720", is_dub=False):

    downloader = Downloader(anime_url, names_url, start_epi, end_epi, is_filler, is_titles, token, threads, directory, gui, resolution, is_dub)
    downloader.download()

def main():

    parser = argparse.ArgumentParser(description="Anime Downloader Command Line Tool")
    argparse.ArgumentParser(description="Help option parcer for Anime Downloader Command Line Tool", add_help=False,
                            formatter_class=argparse.HelpFormatter)

    parser.add_argument("-u", "--url", required=False, help="9Anime.to URL for the anime to be downloaded", dest="url")
    parser.add_argument("-n", "--names", required=False,
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
    parser.add_argument("--nogui", action='store_true', required=False, help="Disable GUI for cli", 
                        dest="nogui")

    args = parser.parse_args()

    titles = False
    if args.title_url:
        titles = True

    directory = args.dir
    if directory != "":
        directory = directory.replace("\\", "/")
        if not directory.endswith("/"):
            directory += "/"

    if args.nogui:
        download(args.url, args.title_url, args.start, args.end, args.isFiller, titles, args.token, args.threads, directory, None)
    else:
        AnimeGUI(Queue()).run()

if __name__ == "__main__":
    #AnimeGUI(Queue()).run()
    main()

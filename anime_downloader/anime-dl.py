from anime_downloader import Anime_Downloader
from anime_downloader.scrapers.nineanime import Anime_Scraper
import warnings
from queue import Queue
from anime_downloader.gui.GUI import Anime_GUI

if __name__ == "__main__" :
    warnings.filterwarnings("ignore")
    Anime_GUI(Queue(), Anime_Downloader, Anime_Scraper).run()
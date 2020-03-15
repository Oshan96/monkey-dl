import Anime_Downloader
import Anime_Scraper
import warnings
from queue import Queue
from gui.GUI import Anime_GUI

if __name__ == "__main__" :
    warnings.filterwarnings("ignore")
    Anime_GUI(Queue(), Anime_Downloader, Anime_Scraper).run()
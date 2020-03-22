import queue
import cloudscraper
import PySimpleGUI as sg
from threading import Thread
from time import sleep
from scrapers.nineanime import Anime_Scraper
from scrapers.fouranime.fouranime_scraper import FourAnimeScraper
from scrapers.nineanime.nineanime_scraper import NineAnimeScraper
from Anime_Downloader import Downloader
from util.name_collector import EpisodeNamesCollector
from util.Color import printer

sg.theme('Dark Amber')


# def execute(downloader, scraper, start_epi, end_epi):
#     scraper.main(start_epi, end_epi, downloader.token)
#     downloader.download()


def download(anime_url, names_url, start_epi, end_epi, is_filler, is_titles, token, threads, directory, gui):
    session = cloudscraper.create_scraper()

    scraper = None

    episodes = []

    anime_url = anime_url.lower()

    # print(anime_url)

    if "9anime.to" in anime_url :
        # scraper = Anime_Scraper
        # scraper.download_9anime_url = anime_url
        # scraper.title_url = names_url
        # scraper.isFiller = is_filler
        # scraper.session = session
        #
        # scraper.main(start_epi, end_epi, token)
        # episodes = scraper.episodes

        scraper = NineAnimeScraper(anime_url, start_epi, end_epi, session, gui, token)

    elif "4anime.to" in anime_url:
        # print("4anime")
        scraper = FourAnimeScraper(anime_url, start_epi, end_epi, session, gui)

        # episodes = scraper.get_direct_links()
        # if episodes:
        #     if is_titles:
        #         episodes = EpisodeNamesCollector(names_url, start_epi, end_epi, is_filler, episodes)
        #
        # else:
        #     gui.gui_queue.put("[ERROR] : Failed to retrieve download links!")
        #     return

    else:
        return

    printer("INFO", "Collecting download links...", gui)
    episodes = scraper.get_direct_links()

    if episodes is None:
        printer("INFO", "Retrying to collect download links...", gui)
        sleep(5)
        episodes = scraper.get_direct_links()

    if episodes:
        if is_titles:
            printer("INFO", "Setting episode titles...", gui)
            episodes = EpisodeNamesCollector(names_url, start_epi, end_epi, is_filler, episodes).collect_episode_names()

        # for episode in episodes:
        #     print(episode.episode, "-", episode.title)

    else:
        printer("ERROR", "Failed to retrieve download links!", gui)
        return

    # print("is titles", is_titles)
    downloader = Downloader(directory, episodes, threads, gui, is_titles)
    downloader.download()


class AnimeGUI:

    def __init__(self, gui_queue):
        self.gui_queue = gui_queue
        self.window = None

    def create_ui(self):
        layout = [

            [sg.Text("General Details", size=(15, 1)), sg.Text("_" * 60, pad=(0, 15))],
            [sg.Text("Anime URL (9anime.to)", text_color="white", size=(25, 1)), sg.InputText(key="anime_url")],
            [sg.Text("Animefillerlist URL", text_color="white", size=(25, 1)), sg.InputText(key="names_url")],
            [sg.Text("Save To", size=(25, 1), text_color="white"), sg.InputText(key="location"), sg.FolderBrowse()],

            [sg.Text("Episodes Details", size=(15, 1)), sg.Text("_" * 60, pad=(0, 15))],
            [sg.Text("From", text_color="white"), sg.InputText(key="start_epi", size=(5, 1)),
             sg.Text("To", text_color="white"), sg.InputText(key="end_epi", size=(5, 1)),
             sg.Text("Download Filler Episodes?", text_color="white"),
             sg.Combo(["Yes", "No"], size=(4, 1), default_value="Yes", key="isFiller"),
             sg.Text("Threads", text_color="white"),
             sg.Spin([i for i in range(1, 21)], initial_value=1, size=(3, 1), key="threads")],
            [],

            [sg.Text("Optional Settings (Fill this if you don't have 2captcha key)", size=(45, 1)),
             sg.Text("_" * 25, pad=(0, 15))],
            [sg.Text("Recaptcha Token (Optional)", text_color="white", size=(25, 1)),
             sg.Multiline(size=(45, 4), key="token")],
            [sg.Column([[sg.Button("Download", size=(10, 1))]], justification="right", pad=(35, 5))],
            [],
            [sg.Text("Messages")],
            [sg.Multiline(size=(None, 8), key="txt_msg", disabled=True)],
            []
        ]

        self.window = sg.Window("Anime Downloader v0.1.1-alpha", layout)

    def check_messages(self, values):
        txt = values["txt_msg"].strip()
        while True:
            try:  # see if something has been posted to Queue
                message = self.gui_queue.get_nowait()
            except queue.Empty:  # get_nowait() will get exception when Queue is empty
                break  # break from the loop if no more messages are queued up
            # if message received from queue, display the message in the Window
            if message:
                txt += "\n" + message
                self.window['txt_msg'].update(txt)
                # do a refresh because could be showing multiple messages before next Read
                self.window.refresh()
                # print(message)

    def run(self):
        self.create_ui()
        while True:
            # wait for up to 100 ms for a GUI event
            event, values = self.window.read(timeout=100)
            if event in (None, 'Exit'):
                break

            if event == "Download":
                anime_url = values["anime_url"]
                names_url = values["names_url"]
                is_titles = True if names_url != "" else False
                is_filler = True if values["isFiller"] == "Yes" else False

                tok = values["token"].rstrip()
                token = tok if tok != "" else None

                directory = values["location"]
                threads = values["threads"]
                start_epi = int(values["start_epi"]) if values["start_epi"] != "" else 1
                end_epi = int(values["end_epi"]) if values["end_epi"] != "" else 9999

                if anime_url == "":
                    self.window['txt_msg'].update("[ERROR!] : Provide Anime URL!")
                    continue

                if directory != "":
                    directory = directory.replace("\\", "/")
                    if not directory.endswith("/"):
                        directory += "/"

                # self.scraper.download_9anime_url = anime_url
                # self.scraper.title_url = names_url
                # self.scraper.isFiller = is_filler
                #
                # self.downloader.titles = is_titles
                #
                # self.downloader.token = token
                #
                # self.downloader.directory = directory
                # self.downloader.threads = threads
                #
                # self.scraper.gui = self
                # self.downloader.gui = self

                # self.window["txt_msg"].update("[INFO] : Download started!")
                self.window["txt_msg"].update("")
                self.window.refresh()

                # thread = Thread(target=execute, args=(self.downloader, self.scraper, start_epi, end_epi), daemon=True)

                thread = Thread(target=download, args=(anime_url, names_url, start_epi, end_epi, is_filler, is_titles, token, threads, directory, self), daemon=True)
                thread.start()

            self.check_messages(values)

        self.window.close()

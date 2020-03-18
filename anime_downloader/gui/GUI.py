import queue
import PySimpleGUI as sg
from threading import Thread

sg.theme('Dark Amber')
downloader = None
scraper = None

def execute(downloader, scraper, start_epi, end_epi) :
    scraper.main(start_epi, end_epi, downloader.token)
    downloader.download()

class Anime_GUI() :

    def __init__(self, gui_queue, downloader, scraper) :
        self.gui_queue = gui_queue
        self.downloader = downloader
        self.scraper = scraper
        self.window = None

    def create_ui(self) :
        layout = [
            
            [sg.Text("General Details",size=(15,1)),sg.Text("_"*60, pad=(0,15))],
            [sg.Text("Anime URL (9anime.to)", text_color="white", size=(25,1)), sg.InputText(key="anime_url")],
            [sg.Text("Animefillerlist URL", text_color="white", size=(25,1)), sg.InputText(key="names_url")],
            [sg.Text("Save To", size=(25,1), text_color="white"), sg.InputText(key="location"), sg.FolderBrowse()],

            [sg.Text("Episodes Details",size=(15,1)),sg.Text("_"*60, pad=(0,15))],
            [sg.Text("From", text_color="white"), sg.InputText(key="start_epi", size=(5,1)), sg.Text("To", text_color="white"), sg.InputText(key="end_epi", size=(5,1)), sg.Text("Download Filler Episodes?", text_color="white"), sg.Combo(["Yes", "No"], size=(4,1), default_value="Yes", key="isFiller"), sg.Text("Threads", text_color="white"), sg.Spin([i for i in range(1,21)],initial_value=1,  size=(3,1), key="threads")],
            [],

            [sg.Text("Optional Settings (Fill this if you don't have 2captcha key)",size=(45,1)),sg.Text("_"*25, pad=(0,15))],
            [sg.Text("Recaptcha Token (Optional)", text_color="white", size=(25,1)), sg.Multiline(size=(45, 4), key="token")],
            [sg.Column([[sg.Button("Download", size=(10,1))]], justification="right", pad=(35,5))],
            [],
            [sg.Text("Messages")],
            [sg.Multiline(size=(None, 8), key="txt_msg", disabled=True)],
            []
        ]

        self.window = sg.Window("Anime Downloader v0.1.1-alpha", layout)

    def check_messages(self, values) :
        txt = values["txt_msg"].strip()
        while True :
            try:                    # see if something has been posted to Queue
                message = self.gui_queue.get_nowait()
            except queue.Empty:     # get_nowait() will get exception when Queue is empty
                break               # break from the loop if no more messages are queued up
            # if message received from queue, display the message in the Window
            if message:
                txt += "\n" + message
                self.window['txt_msg'].update(txt)
                # do a refresh because could be showing multiple messages before next Read
                self.window.refresh()
                # print(message)

    def run(self) :
        self.create_ui()
        while True :
            # wait for up to 100 ms for a GUI event
            event, values = self.window.read(timeout=100)
            if event in (None, 'Exit'):
                break

            if event == "Download" :
                self.scraper.download_9anime_url = values["anime_url"]
                self.scraper.title_url = values["names_url"]

                if values["names_url"] != "" :
                    self.downloader.titles = True

                if values["isFiller"] == "Yes":
                    self.scraper.isFiller = True
                else :
                    self.scraper.isFiller = False

                tok = values["token"].rstrip()
                
                if tok != "":
                    self.downloader.token = tok

                directory = values["location"]

                if directory != "" :
                    directory = directory.replace("\\", "/")
                    if not directory.endswith("/") :
                        directory+="/"

                self.downloader.directory = directory
                self.downloader.threads = values["threads"]

                self.scraper.gui = self
                self.downloader.gui = self

                # self.window["txt_msg"].update("[INFO] : Download started!")
                self.window.refresh()

                start_epi = 1
                end_epi=9999

                if values["start_epi"] != "":
                    start_epi = int(values["start_epi"])

                if values["end_epi"] != "":
                    end_epi = int(values["end_epi"])

                thread = Thread(target=execute, args=(self.downloader, self.scraper, start_epi, end_epi), daemon=True)
                thread.start()
                
            self.check_messages(values)

        self.window.close()


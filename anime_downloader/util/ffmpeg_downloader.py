from shutil import which
from util.Color import printer
import subprocess
from platform import system


class FFMPEGDownloader:
    def __init__(self, episode, directory, gui=None):
        self.episode = episode
        self.directory = directory
        self.gui = gui

    def __clean_file_name(self, file_name):
        for c in r'[]/\;,><&*:%=+@#^()|?^':
            file_name = file_name.replace(c, '')

        return file_name

    def download(self):
        # print("FFMPEG", which("ffmpeg"))
        if self.episode.download_url is None:
            printer("ERROR", "Download URL is not set for " + self.episode.episode + ", skipping...", self.gui)
            return

        if which("ffmpeg") is None:
            printer("ERROR", "FFMPEG not found! Please install and add to system path to download!", self.gui)
            return

        printer("INFO", "Downloading " + self.episode.episode + "...", self.gui)

        if system() == "Windows":
            self.episode.title = self.__clean_file_name(self.episode.title)

        file_name = self.directory + self.episode.episode + " - " + self.episode.title + ".mp4"

        code = subprocess.call(
            ['ffmpeg', '-i', self.episode.download_url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', file_name])

        if code == 0:
            printer("INFO", self.episode.episode + " finished downloading...", self.gui)
        else:
            printer("ERROR", self.episode.episode + " failed to download!", self.gui)

"""Automatic updater for Monkey-DL executable versions (Windows).

Updater will check for the version of the latest release against the current installed version and notify whether a
new update is available The Updater class will be used to create the executable (Windows) which will download the
latest executable version from GitHub releases page.

Note: The executable version of the Updater will be downloading the latest release executable version and will write
the binary data to the existing monkey-dl exe. So it is strongly advice not to use the updater or any monkey-dl
executable other than from the original monkey-dl repository release page, which is
https://github.com/Oshan96/monkey-dl/releases

"""

import requests
import traceback
from io import BytesIO
from zipfile import ZipFile
from pkg_resources import parse_version
from util.Color import printer
from monkey_dl import __version__

GITHUB_RELEASES_API = "https://api.github.com/repos/Oshan96/monkey-dl/releases"
GITHUB_RELEASE_TAG_API = "https://api.github.com/repos/Oshan96/monkey-dl/releases/tags/{tag}"


def get_update_tag():
    releases_data = requests.get(GITHUB_RELEASES_API).json()
    for release in releases_data:
        if parse_version(release["tag_name"]) > parse_version(__version__):
            return release["tag_name"]

    return None


class Updater:
    def __init__(self, gui=None):
        self.gui = gui

    def update(self):
        tag_name = None

        printer("INFO", "Checking for new Monkey-DL version...", self.gui)
        try:
            tag_name = get_update_tag()
        except Exception:
            printer("ERROR", "Error occurred while calling GitHub API", self.gui)

        if tag_name is None:
            printer("INFO", "Monkey-DL is upto date!", self.gui)
            return False

        try:
            release_data = requests.get(GITHUB_RELEASE_TAG_API.format(tag=tag_name)).json()
            download_url = release_data["assets"][0]["browser_download_url"]

            printer("INFO", "Downloading Monkey-DL {tag}...".format(tag=tag_name))
            zip_data = requests.get(download_url).content

            zip_file = ZipFile(BytesIO(zip_data))
            monkey_dl_content = zip_file.open("monkey-dl.exe").read()

            printer("INFO", "Updating Monkey-DL to {tag}".format(tag=tag_name))
            with open("monkey-dl.exe", "wb") as monkey:
                monkey.write(monkey_dl_content)

        except Exception:
            print(traceback.format_exc())
            printer("ERROR", "Failed to update Monkey-DL! Please download {tag} manually!".format(tag=tag_name), self.gui)

            return False

        return True


# if __name__ == "__main__":
#     Updater().update()

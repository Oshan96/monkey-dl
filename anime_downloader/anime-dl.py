import os
import sys
import warnings
from queue import Queue
from gui.GUI import AnimeGUI

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    # activate color codes
    if sys.platform.lower() == "win32":
        os.system("color")

    AnimeGUI(Queue()).run()

import warnings
from queue import Queue
from gui.GUI import AnimeGUI

if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    AnimeGUI(Queue()).run()

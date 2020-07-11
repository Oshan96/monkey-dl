from queue import Queue
from gui.GUI import AnimeGUI
from cli.CLI import AnimeCLI

def main():

    noGui = AnimeCLI().run()

    if not noGui:
        AnimeGUI(Queue()).run()

if __name__ == "__main__":
    main()

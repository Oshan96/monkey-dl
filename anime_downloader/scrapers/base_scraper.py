class BaseScraper:
    def __init__(self, url, start_episode, end_episode, session, gui=None):
        self.url = url
        self.start_episode = start_episode
        self.end_episode = end_episode
        self.session = session
        self.gui = gui

        self.episodes = []

    def get_direct_links(self):
        raise NotImplementedError

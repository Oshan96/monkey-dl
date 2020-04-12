import cloudscraper
class BaseExtractor:

    def __init__(self, url, session):
        self.url = url
        if session is None:
            self.session = cloudscraper.create_scraper()
        else:
            self.session = session

    def extract_page_content(self):
        video_page = self.session.get(self.url)
        return video_page.text

    def extract_direct_url(self):
        raise NotImplementedError

    def direct_link(self):
        return self.extract_direct_url()
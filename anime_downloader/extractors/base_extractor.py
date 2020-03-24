class BaseExtractor:

    def __init__(self, url, session):
        self.url = url
        self.session = session

    def extract_page_content(self):
        video_page = self.session.get(self.url).content
        return video_page.decode('utf-8')

    def extract_direct_url(self):
        raise NotImplementedError

    def direct_link(self):
        return self.extract_direct_url()
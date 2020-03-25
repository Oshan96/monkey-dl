import re
from extractors.base_extractor import BaseExtractor


class Mp4UploadExtractor(BaseExtractor):

    def __init__(self, url, session):
        super().__init__(url, session)

    def extract_direct_url(self):
        page_content = self.extract_page_content()

        www_base = re.search("false\|(.*)\|devicePixelRatio", page_content).group(1)
        id_port = re.search("video\|(.*)\|(.*)\|src", page_content)
        url_id = id_port.group(1)
        port = id_port.group(2)

        direct_url = "https://{}.mp4upload.com:{}/d/{}/video.mp4".format(www_base, port, url_id)

        return direct_url


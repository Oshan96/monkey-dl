import re
from extractors.base_extractor import BaseExtractor


class JWPlayerExtractor(BaseExtractor):

    def __init__(self, url, session):
        super().__init__(url, session)

    def extract_sources(self):
        page_content = self.extract_page_content()

        link_sources = [match.group(1) for match in
                        re.finditer("{\s*file\s*:\s*[\"\']\s*([https][^\"\']+)", page_content)]

        return link_sources

    def extract_direct_url(self):
        direct_links = self.extract_sources()

        if len(direct_links) > 0 :
            #check if direct links or hls links
            if ".m3u8" not in direct_links[0] :
                #return the first direct link
                return direct_links[0]
        else:
            return None


# if __name__ == "__main__":
#     data = "sources: [{file:\"http://localhost/srt/43534234/viral022018SD.MP4\",label:\"SD\",type: \"video/mp4\"}," \
#            "{file:\"https://localhost/srt/43534234/viral022018HD.MP4\",label:\"HD\",type: \"video/mp4\"," \
#            "default: true}] "
#     print(JWPlayerExtractor(None, cloudscraper.create_scraper()).extract_sources(data))

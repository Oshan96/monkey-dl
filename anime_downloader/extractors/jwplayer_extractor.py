import re
from extractors.base_extractor import BaseExtractor


class JWPlayerExtractor(BaseExtractor):

    def __init__(self, url, session):
        super().__init__(url, session)

    def extract_sources(self):
        page_content = self.extract_page_content()

        link_sources = [match.group(1) for match in
                        re.finditer("{\s*file\s*:\s*[\"\']\s*([htps][^\"\']+)", page_content)]

        return link_sources

    def extract_direct_url(self):
        direct_links = self.extract_sources()

        if len(direct_links) > 0:
            # return the first direct link
            return direct_links[0]
        else:
            return None

    # if the given resolution is not found, the first available link would be given
    def get_resolution_link(self, master_url, resolution):
        count = 0
        content = self.session.get(master_url).text
        # print(content.split("\n"))
        data_list = content.split("\n")

        link = None

        for index, data in enumerate(data_list):
            res = re.search("RESOLUTION=(.*)x(.*)", data)
            if res is not None:
                # print(res.group(1), res.group(2).split(",")[0])
                k = res.group(2).split(",")[0]
                if k == resolution:
                    # print(k)
                    # print(data_list[index+1])
                    return data_list[index+1]   # next one will be the link

                if count == 0:
                    # print("First :", k)
                    link = data_list[index+1]   # save the first result

                count += 1

        return link

    def extract_stream_link(self, resolution="720"):
        link = self.extract_direct_url()

        print("Master Link : " + link)

        if "master.m3u8" in link:
            link = self.get_resolution_link(link, resolution)
            print("Index Link : " + link)

        return link


if __name__ == "__main__":
    import cloudscraper

    # data = "sources: [{file:\"http://localhost/srt/43534234/viral022018SD.MP4\",label:\"SD\",type: \"video/mp4\"}," \
    #        "{file:\"https://localhost/srt/43534234/viral022018HD.MP4\",label:\"HD\",type: \"video/mp4\"," \
    #        "default: true}] "
    # print(JWPlayerExtractor(None, cloudscraper.create_scraper()).extract_sources(data))

    # print(JWPlayerExtractor("https://www1.animeultima.to/faststream/2336",
    #                         cloudscraper.create_scraper()).extract_direct_url())

    print(JWPlayerExtractor("https://www1.animeultima.to/faststream/2336",
                            cloudscraper.create_scraper()).extract_stream_link("240"))

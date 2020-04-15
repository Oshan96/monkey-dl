import re
from extractors.base_extractor import BaseExtractor


class JWPlayerExtractor(BaseExtractor):

    def __init__(self, url, session):
        super().__init__(url, session)

    def extract_sources(self, page_content=None):
        if page_content is None:
            page_content = self.extract_page_content()

        # print(page_content)

        link_sources = [match.group(1) for match in
                        re.finditer("{\s*file\s*:\s*[\"\']\s*([htps][^\"\']+)", page_content)]

        return link_sources

    def extract_direct_url(self):
        print("extracting direct stream links")
        direct_links = self.extract_sources()

        # print(direct_links)

        if len(direct_links) > 0:
            # return the first direct link
            return direct_links[0]
        else:
            return None

    # if the given resolution is not found, the first available link would be given
    def get_resolution_link(self, master_url, resolution):
        count = 0
        try:
            content = self.session.get(master_url).text
        except:
            print("retry")
            content = self.session.get(master_url).text

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
        print("Extracting stream link")
        link = self.extract_direct_url()

        print("Master Link : " + link)

        if "master.m3u8" in link:
            link = self.get_resolution_link(link, resolution)
            print("Index Link : " + link)

        return link


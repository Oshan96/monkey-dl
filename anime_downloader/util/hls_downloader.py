import re
from util.Color import printer
from Crypto.Cipher import AES


class HLSDownloader:
    def __init__(self, episode, directory, session, gui=None):
        self.episode = episode
        self.directory = directory
        self.session = session
        self.gui = gui
        self.count = 0

    def __get_default_iv(self):
        """When IV is not passed, m3u8 use incremental 16byte iv key starting from 1 for each segment"""
        self.count += 1
        return self.count.to_bytes(16, 'big')

    def __decrypt(self, data, key, iv=None):
        if iv is None:
            iv = self.__get_default_iv()  # get the default iv value for the segment

        # print(iv)
        decryptor = AES.new(key, AES.MODE_CBC, IV=iv)
        return decryptor.decrypt(data)

    def __collect_stream_data(self, ts_url):
        return self.session.get(ts_url).content

    def __is_encrypted(self, m3u8_data):
        method = re.search('#EXT-X-KEY:METHOD=(.*),', m3u8_data)
        if method is None:
            return False

        if method.group(1) == "NONE":
            return False

        return True

    def __collect_uri_iv(self, m3u8_data):
        # print(m3u8_data)
        uri_iv = re.search('#EXT-X-KEY:METHOD=AES-128,URI="(.*)",IV=(.*)', m3u8_data)

        if uri_iv is None:
            uri_data = re.search('#EXT-X-KEY:METHOD=AES-128,URI="(.*)"', m3u8_data)
            return uri_data.group(1), None

        uri = uri_iv.group(1)
        iv = uri_iv.group(2)

        return uri, iv

    def __collect_ts_urls(self, m3u8_data):
        urls = [url.group(0) for url in re.finditer("https://(.*)\.ts(.*)", m3u8_data)]
        if len(urls) == 0:
            print("Relative paths")
            base_url = re.search("(.*)/\S+\.m3u8", self.episode.download_url).group(1)
            urls = [base_url + "/" + url.group(0) for url in re.finditer("(.*)\.ts(.*)", m3u8_data)]

        return urls

    def download(self):
        key = ""
        iv = None

        print(self.episode.download_url)
        m3u8_data = self.session.get(self.episode.download_url).text

        is_encrypted = self.__is_encrypted(m3u8_data)
        if is_encrypted:
            key_uri, iv = self.__collect_uri_iv(m3u8_data)
            # print("uri, iv :", key_uri, iv)
            key = self.__collect_stream_data(key_uri)
            # print("key :", key)

        ts_urls = self.__collect_ts_urls(m3u8_data)
        # print("ts_urls :", ts_urls)

        with open(self.directory + self.episode.title + ".mp4", "wb") as epi_file:
            for ts_url in ts_urls:
                print("Processing ts file :", ts_url)
                ts_data = self.__collect_stream_data(ts_url)
                # print("ts data:", ts_data)
                if is_encrypted:
                    # print("encrypted")
                    ts_data = self.__decrypt(ts_data, key, iv)
                    # print("decrypted")
                # print("writing")
                epi_file.write(ts_data)

# if __name__ == "__main__":
#     import cloudscraper as cs
#     from util.Episode import Episode
#     session = cs.create_scraper()
#
#     epi = Episode("Test", "Test")
#     epi.download_url = "https://v.vrv.co/evs/cf73f5561410a8a7e412491991f0d508/assets/9c7l0i4fq5tnq7u_1055213.mp4/index-v1-a1.m3u8?Policy=eyJTdGF0ZW1lbnQiOlt7IlJlc291cmNlIjoiaHR0cHM6Ly92LnZydi5jby9ldnMvY2Y3M2Y1NTYxNDEwYThhN2U0MTI0OTE5OTFmMGQ1MDgvYXNzZXRzLzljN2wwaTRmcTV0bnE3dV8qIiwiQ29uZGl0aW9uIjp7IkRhdGVMZXNzVGhhbiI6eyJBV1M6RXBvY2hUaW1lIjoxNTg2NjMyOTcyfX19XX0_&Signature=J6o4tQBJKxqNc95v5dhkT7mFEVPQwDZLMBBNsqf2JGcDPCyWvWHunR6nsPSgeWT5nVGuPx2o2fh3OrAJERtQuRMJDpUSCZzOX0Jyajvwb6ot9SAuusXKg4nO7em~CiF2MqQURSChhLHPhiEEmUPD0wlB5WzVWnPg9XxLIX0RMgIXARtDhRrlvL0K-oXEJIv2IWyKe9MoTy99lj1vZmeNy4WKC~opWfXImvRmRReGQyi1Kvr6Wl6fll6oPNFnqq~2CBGPNB5TFQlDr4TnZPHcJasoN3m9OMJuga9SAXi0Td7-klw78dge4z2leQC88QA9aFFGDHqnevDecjAyIQEPZA__&Key-Pair-Id=APKAJMWSQ5S7ZB3MF5VA"
#
#     HLSDownloader(epi, "", session).download()

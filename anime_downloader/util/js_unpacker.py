import jsbeautifier as js
from bs4 import BeautifulSoup
from extractors.jwplayer_extractor import JWPlayerExtractor


class JsUnpacker:
    def __init__(self):
        self.jwp_extractor = JWPlayerExtractor(None, None)

    def eval(self, func):
        val = js.beautify(func)
        return val

    def extract_link(self, func):
        src = ""
        data = self.eval(func)
        # print(data)
        if "jwplayer" in data:
            print("jwplayer source will be returned")
            links = self.jwp_extractor.extract_sources(data)
            if links is not None and len(links) > 0:
                src = links[0]
            else:
                print("no sources found")
                return None

        else:
            print("Any anchor href will be returned")
            anch = BeautifulSoup(data, "html.parser").find("a")
            if anch is not None:
                src = anch['href'].replace('\"', '').replace('\'', '').replace('\\', '')
            else:
                print("No anchor links found")
                return None

        # print(src)
        return src

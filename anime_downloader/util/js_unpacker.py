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

# if __name__ == "__main__":
#     fun = '''
#     eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('3 9="5://1d.r.2/i.o.2/f/8/e.j?u=y%v.F.z.2&A=B&C=D%x%E%G%H%I%J%K%L%M%w%k%l%m%a%a";3 c="5://p-q-h.i.2/s/f/8/e.j/O.15";3 4=[{b:9},{b:c}];!6 t(){17{!6 t(n){1===(""+n/n).N&&n%19!=0||6(){}.1a("1b")(),t(++n)}(0)}1c(n){1e(t,1f)}}();3 7=1g(\'7\');7.1h({1i:\'16 14 (8)<P /><g 13="12-11:10;">Z 1</g>\',Y:\'d%\',X:\'d%\',W:\'5://V.U.T/h-S/R.Q\',18:{},4:4,});',62,81,'||com|var|sources|https|function|player|dub|fone|3D|file|ftwo|100|1_1807|116|span|vod|auengine|mp4|2Fo|2B1m9o4E21cFRaGmn6sqip5a0cGoab1lPjNlUB7s07TRdZ|2BVFXLfoXNCRLQ||appspot|s1|na|googleapis|hls2||GoogleAccessId|40auengine|2Bdb6DVVQ7nTjJ9jgqnmJmEHSdEmv6019e0YBwh|2BsspInuB|auevod|gserviceaccount|Expires|1586640060|Signature|SO9JeiA|2FZljXmaCZFHiwn1miyMU|iam|2FYBkDGoICGeUlaWqpe20SqAHBnillgfl03rc|2FxeI3MoCQn4Eps3gaxHdgp7GjXPIRWxHVAr1uMzuX5RiNvLGarTrndZ|2BxL9B0kpK2rgHf5BEQoQgwuAOhwltn30ikKP0nNYMQj64mErafXWkmvP90t8Qhom|2BUOhgjXpJcZqW9fOly|2BDqttGgU96b|2F0Z3u0m1rYGvtpYJ8M9QcBZM|2F|length|playlist|br|jpg|vs3b1Z2XacICszjz|thumbnails|tv|animeultima|cdn|image|height|width|Episode|12px|size|font|style|Piece|m3u8|One|try|cast|20|constructor|debugger|catch|storage|setTimeout|1e3|jwplayer|setup|title'.split('|'),0,{}))
#     '''
#
#     print(JsUnpacker().extract_link(fun))
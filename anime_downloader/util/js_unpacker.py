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

        print(src)
        return src

if __name__ == "__main__":
    JsUnpacker().extract_link('''eval(function(p,a,c,k,e,d){e=function(c){return(c<a?'':e(parseInt(c/a)))+((c=c%a)>35?String.fromCharCode(c+29):c.toString(36))};if(!''.replace(/^/,String)){while(c--){d[e(c)]=k[c]||e(c)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('2.A="j+i/h==";2(\'g\').f({e:[{d:"c://b.a.4/8-7-6.k.4/m.l.o/1-3/1-3-p-0.q",r:"0"}],s:{},t:\'u:9\',v:\'w%\',x:\'y\',z:{n:"5"},});',37,37,'1080p|One|jwplayer|Piece|com|seven|254209|theater|linear||googleapis|storage|https|file|sources|setup|my_video|TBfiK4s0vvYg|axNzjIp|Ywok59g9j93GtuSU7|appspot|4animu|v3|name|me|532|mp4|label|cast|aspectratio|16|width|100|preload|none|skin|key'.split('|'),0,{}))''')
    JsUnpacker().extract_link('''eval(function(p,a,c,k,e,d){e=function(c){return c.toString(36)};if(!''.replace(/^/,String)){while(c--){d[c.toString(a)]=k[c]||c.toString(a)}k=[function(e){return d[e]}];e=function(){return'\\w+'};c=1};while(c--){if(k[c]){p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])}}return p}('5.7(\'<a 1=\\"8\\" 9=\\"b://c.d.4/e-f-6.h.4/g.k.l/3-2/3-2-m-n.o\\"><i 1=\\"0 0-p\\"></i> j</a>\');',26,26,'fa|class|Piece|One|com|document|254209|write|mirror_dl|href||https|storage|googleapis|linear|theater|v3|appspot||Download|4animu|me|532|1080p|mp4|download'.split('|'),0,{}))''')
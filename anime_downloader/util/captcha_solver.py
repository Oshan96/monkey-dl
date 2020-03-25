from time import sleep


class TwoCaptchaSolver:
    def __init__(self, url, site_key, api_key, session):
        self.url = url
        self.site_key = site_key
        self.api_key = api_key
        self.session = session

    def solve(self):
        try:
            captcha_id = \
                self.session.post(
                    "http://2captcha.com/in.php?key={}&method=userrecaptcha&googlekey={}&pageurl={}&invisible=1"
                        .format(self.api_key, self.site_key, self.url)).text.split('|')[1]

            recaptcha_answer = self.session.get(
                "http://2captcha.com/res.php?key={}&action=get&id={}".format(self.api_key, captcha_id)).text

            while 'CAPCHA_NOT_READY' in recaptcha_answer:
                sleep(5)
                recaptcha_answer = self.session.get(
                    "http://2captcha.com/res.php?key={}&action=get&id={}".format(self.api_key, captcha_id)).text

            recaptcha_answer = recaptcha_answer.split('|')[1]

            # print("[Recaptcha answer] : {",recaptcha_answer,"}")
            return recaptcha_answer

        except Exception:
            return None

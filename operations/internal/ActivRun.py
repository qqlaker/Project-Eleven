import requests
import pickle
import os

from service.Runurl import Runurl
from cairosvg import svg2png
from twocaptcha import TwoCaptcha


class ActiveRun:
    @staticmethod
    def activation(login: str, promo_code: str, que, proxy=None):
        # preparing
        if f'cookies_{login}.pkl' in os.listdir("temp/cookies"):
            payload = pickle.load(open(f'temp/cookies/cookies_{login}.pkl', 'rb'))
        else:
            with open("../../temp/ACTIV.txt", "a+") as f:
                f.write(f"{login} " + "NO COOKIE FILE" + "\n")
            que.put([login, "NO COOKIE FILE"])
            return

        proxies = None
        if proxy is not None:
            proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }

        # receiving captcha image
        url = f"https://api.{Runurl.DOMEN}/captcha"
        r = requests.get(url=url, headers=payload, proxies=proxies)
        r = r.text
        print(r)
        left = r.find('<path d=')
        right = r.find('fill="none"/>')
        sub = r[left:right + 13]
        r = r[r.find("<svg xmlns"):].replace(sub, '').replace('"}', '').replace('\\', '')
        print(login)
        svg2png(bytestring=r, write_to=f'captchas/captcha_{login}.png')
        quit()

        # captcha solving
        solver = TwoCaptcha('91338054e656fd811a92592021cbe6a6')
        print("captcha solver: " + login)
        result = solver.normal(f"captchas/captcha_{login}.png", minLength=3, maxLength=4, caseSensitive=1, lang='en')
        captcha = result['code']
        print("login + captcha:", login, captcha)

        # activation request
        url = "https://api.csgo2.run/discount"
        data = {"code": promo_code, "captchaCode": captcha}
        r = requests.post(url=url, headers=payload, json=data, proxies=proxies)
        print(r.headers)
        with open("../../temp/ACTIV.txt", "a+") as f:
            f.write(f"{login} " + r.text + "\n")
        que.put([login, r.text])
        return

import datetime
import time
import httplib2
import requests
import vk_api
import urllib3
import os

from PIL import Image
from twocaptcha.api import ApiException
from twocaptcha import TwoCaptcha

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
VK_RUN_TOKENS = ["vk1.a.ijEYizChi86rI2248V6-980DBU5Sp3at_nGaoyQdcMRB6OGdKzfFuSh4dUwOlY5qQQhO"
                 "kogvjykKLcHn3MbQ2Zh8l0CM7DZyp9fAovhm119H-IwFZ9mdy0Rotnz1BD7YBUoCBUz0GAiuFc"
                 "EiBlLOC6CTmrI6gW4iT73oTJIlT4lH4EnWihUNMMbV0UVdAH_aOr64kj2WYPPEZklBjc6X6g"]
TOKEN = VK_RUN_TOKENS[0]
SESSION = vk_api.VkApi(token=TOKEN)


class GetPromo:
    # Временное решение через rucaptcha. Для 100% распознавания отправляй себе в тг и решай сам, либо cloud vision :)
    def get_promo_from_img(self, path):
        box = (220, 570, 760, 690)
        im = Image.open(path)
        im = im.crop(box)
        pathpng = path[:-3] + "png"
        im.show()
        print(pathpng)
        im.save(pathpng)
        solver = TwoCaptcha('2499c4c206868f7632c9a229a181ad85')
        attempts = 0
        result = ""
        while attempts < 3:
            attempts += 1
            try:
                print("a1")
                result = solver.normal(pathpng)
                break
            except ApiException as e:
                print("GetPromo line 41 |", e)
        print("a2")
        if result:
            promo = result["code"]
        else:
            promo = None
        os.remove(path)
        os.remove(pathpng)
        return promo

    def run_vk(self):
        while True:
            time.sleep(0.5)
            if datetime.datetime.now().time() > datetime.datetime.strptime("21:00:00", "%H:%M:%S").time():
                break
        allowed_phrases = ['активаций']
        temp_bool = True
        io = 0
        tim = (17.4 / len(VK_RUN_TOKENS))
        cur_token_run = VK_RUN_TOKENS[io]
        time.sleep(5)
        while temp_bool:
            time.sleep(5)  # tim
            # owner_id=-185858278
            rurl = f'https://api.vk.com/method/wall.get?owner_id=-212752887&domain=https://vk.com/csgorun_net&count=2&filter=all&access_token={cur_token_run}&v=5.131'
            response = requests.get(rurl, verify=False)
            resp = response.json()
            if response.status_code == 10:
                print('VK server error... await...')
                time.sleep(120)
            if '"error_code":29' in response.text:
                if io < len(VK_RUN_TOKENS):
                    io += 1
                    cur_token_run = VK_RUN_TOKENS[io]
                    continue
                else:
                    print('csgorun_vk_wall | VK акки израсходованны')
            items = resp['response']['items']
            for item in items:
                # print(item['attachments'][0]['photo']['sizes'])
                post_date = str(item['date'])[:10]
                post_date = datetime.datetime.fromtimestamp(int(post_date))
                if datetime.datetime.now() - post_date <= datetime.timedelta(minutes=30):
                    if any(s in item['text'] for s in allowed_phrases):
                        for size in item['attachments'][0]['photo']['sizes']:
                            if int(size['height']) == 1000:
                                url = size['url']
                                h = httplib2.Http('.cache')
                                response, content = h.request(url)
                                path = f'temp/promo_csgorun{datetime.datetime.now().date()}.jpg'
                                with open(path, 'wb') as out:
                                    out.write(content)
                                promo = self.get_promo_from_img(path)
                                print("promo:", promo)
                                if promo is None:
                                    return None
                                onlyfiles = [f for f in os.listdir("../../temp") if os.path.isfile(os.path.join(
                                    "../../temp", f))]
                                if 'last_code.txt' in onlyfiles:
                                    with open('../../temp/last_code.txt', 'r+') as f:
                                        a = f.readline().strip('\n')
                                else:
                                    a = ''
                                print("212")
                                if a != str(promo):
                                    print("313")
                                    with open('../../temp/last_code.txt', 'w+') as f:
                                        f.write(str(promo))
                                    return promo
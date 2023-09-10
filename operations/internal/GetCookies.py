import json
import pickle
import datetime
import time
import os

from func_timeout import func_timeout, FunctionTimedOut
from selenium.webdriver.common.by import By
from service.Steamauth import Steamauth
from service.Runurl import Runurl
from os import listdir
from os.path import isfile, join


def process_browser_logs_for_network_events(logs):
    for entry in logs:
        log = json.loads(entry["message"])["message"]
        if (
            "Network.response" in log["method"]
            or "Network.request" in log["method"]
            or "Network.webSocket" in log["method"]
        ):
            yield log


class GetCookies(Steamauth):
    @staticmethod
    def check_date():
        onlyfiles = [f for f in listdir("../../temp") if isfile(join("../../temp", f))]
        if 'lastCookieDate.txt' in onlyfiles:
            with open("../../temp/lastCookieDate.txt", "r") as f:
                line = f.readline().strip('\n')
                if line != '':
                    last_cookie_date = datetime.datetime.strptime(line, '%Y-%m-%d').date()
                else:
                    return True
            if (datetime.datetime.now().date()-last_cookie_date) > datetime.timedelta(days=15):
                return True
            else:
                return False
        with open("../../temp/lastCookieDate.txt", "w+") as f:
            pass
        return True

    def __init__(self, _logins):
        self.logins = _logins

    def cookies(self, _login, _password, _driver_cookies):
        print(f"GetCookies | Получаем cookie для {_login}...")
        if self.is_element_present(_driver_cookies, By.CLASS_NAME, 'switcher__content'):
            switcher = _driver_cookies.find_element_by_class_name("switcher__content")
            switcher.click()
        lbtn = _driver_cookies.find_element_by_class_name("btn.btn--green.steam-login")
        lbtn.click()

        if not Steamauth.login(self, _driver_cookies, _login, _password):
            return False

        # Нужно чтобы на странице рана успела обновиться кнопка логина, иначе её детектит
        t = 0
        while self.is_element_present(_driver_cookies, By.CLASS_NAME, "btn.btn--green.steam-login"):
            time.sleep(2)
            t += 2
            if t >= 20:
                break

        if self.is_element_present(_driver_cookies, By.CLASS_NAME, "btn.btn--green.steam-login"):
            print(f"GetCookies | Аккаунт в бане csgorun | {_login}")
            return True

        logs = _driver_cookies.get_log("performance")
        events = process_browser_logs_for_network_events(logs)
        auth = None

        for event in events:
            if event['method'] == 'Network.requestWillBeSentExtraInfo':
                try:
                    auth = {'authorization': event['params']['headers']['authorization']}
                except Exception as e:
                    pass
        if auth:
            pickle.dump(auth, open(f'temp/cookies/cookies_{_login}.pkl', 'wb+'))
            return True
        else:
            return False

    # logins: list [0]login, [1]password
    def main_rec(self, is_all=True):
        if not is_all:
            temp_list = []
            for i in range(len(self.logins)):
                if f'cookies_{self.logins[i][0]}.pkl' not in os.listdir("temp/cookies"):
                    temp_list.append(self.logins[i])
            self.logins = temp_list
        while len(self.logins) != 0:
            driver_cookies = self.driverinit(Runurl.RUNURL, proxy_for_login=self.logins[0][0])
            try:
                success = func_timeout(40, self.cookies, args=(self.logins[0][0], self.logins[0][1], driver_cookies,))
                if success:
                    self.logins.remove(self.logins[0])
                    print("GetCookies | Получено")
                driver_cookies.quit()
            except FunctionTimedOut:
                driver_cookies.quit()
            except Exception as e:
                print(f"GetCookies main | {e}")
                driver_cookies.quit()

        with open('../../temp/lastCookieDate.txt', 'w+') as F:
            F.write(str(datetime.datetime.now().date()))
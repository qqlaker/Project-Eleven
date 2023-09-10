import json
import os
import time
import pathlib
import urllib
import selenium.webdriver.support.expected_conditions as EC
import undetected_chromedriver as undchromedriver
import zipfile
import os

from selenium.common.exceptions import StaleElementReferenceException
from PIL import Image
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from steampy.guard import generate_one_time_code
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options


class Steamauth(object):

    def is_element_present(self, driver_steam: Chrome, id_type, id_locator):
        try:
            element = WebDriverWait(driver_steam, 3).until(EC.presence_of_element_located((id_type, id_locator)))
            element_found = True
        except:
            element_found = False
        return element_found

    def getcode(self, share):
        shared_secret = share
        one_time_authentication_code = generate_one_time_code(shared_secret)
        return one_time_authentication_code

    def driverinit(self, url=None, proxy_for_login=None):

        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        chrome_driver_path = str(pathlib.Path(__file__).parent.absolute()) + '/chromedriver.exe'
        chrome_options = Options()

        # proxy
        if proxy_for_login:
            with open("../config/proxy.txt", "r") as f:
                for line in f:
                    login, proxy = line.split(" ")
                    if login == proxy_for_login:
                        # login:password@ip:port
                        proxy_left, proxy_right = proxy.split("@")
                        proxy_host, proxy_port = proxy_right.split(":")
                        proxy_user, proxy_pass = proxy_left.split(":")

                        manifest_json = """
                        {
                            "version": "1.0.0",
                            "manifest_version": 2,
                            "name": "Chrome Proxy",
                            "permissions": [
                                "proxy",
                                "tabs",
                                "unlimitedStorage",
                                "storage",
                                "<all_urls>",
                                "webRequest",
                                "webRequestBlocking"
                            ],
                            "background": {
                                "scripts": ["background.js"]
                            },
                            "minimum_chrome_version":"76.0.0"
                        }
                        """
                        background_js = """
        let config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (proxy_host, proxy_port, proxy_user, proxy_pass)

                        plugin_file = '../temp/proxy_auth_plugin.zip'
                        with zipfile.ZipFile(plugin_file, 'w') as zp:
                            zp.writestr('manifest.json', manifest_json)
                            zp.writestr('background.js', background_js)
                        chrome_options.add_extension(plugin_file)

        #chrome_options.add_argument('headless')
        driver = undchromedriver.Chrome(options=chrome_options, executable_path=chrome_driver_path)
        driver.maximize_window()
        if url:
            driver.get(url)
        return driver

    def login(self, _driver_steam, _login, _password):

        def CheckTwofactorauthMessage():
            def presense_of_element():
                element_found = True
                try:
                    WebDriverWait(_driver_steam, 0).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'twofactorauth_message'))
                    )
                except:
                    element_found = False
                return element_found

            while presense_of_element():
                    try:
                        if any(message.is_displayed() for message in
                               _driver_steam.find_elements_by_class_name('twofactorauth_message')):
                            return False
                    except StaleElementReferenceException:
                        if any(message.is_displayed() for message in
                               _driver_steam.find_elements_by_class_name('twofactorauth_message')):
                            return False

                    if 'steamcommunity.com/openid' not in _driver_steam.current_url:
                        return True

        while True:
            if self.is_element_present(_driver_steam, By.ID, 'steamAccountName'):
                _driver_steam.find_element_by_id('steamAccountName').send_keys(_login)
                _driver_steam.find_element_by_id('steamPassword').send_keys(_password)
                _driver_steam.find_element_by_class_name('btn_green_white_innerfade').click()
                _driver_steam.implicitly_wait(10)
                break
            else:
                if self.is_element_present(_driver_steam, By.CLASS_NAME, 'OpenID_loggedInAccount'):
                    _driver_steam.find_element_by_class_name('btn_green_white_innerfade').click()
                    break

        while 'steamcommunity.com/openid' in _driver_steam.current_url:
            if _driver_steam.find_element_by_id('login_twofactorauth_message_entercode').is_displayed():
                if self.is_element_present(_driver_steam, By.ID, 'twofactorcode_entry'):
                    print(f'Steamauth | Введите Steam Guard код | {_login}')
                    try:
                        a = False
                        mafiles = os.listdir('mafiles')
                        for mafile in mafiles:
                            with open(f'mafiles/{mafile}', 'r') as f:
                                json_mafile = json.load(f)
                                cur_login = json_mafile['account_name']
                                if _login == cur_login:
                                    a = True
                                    shared = json_mafile['shared_secret']
                                    tfc = self.getcode(shared)
                                    print('>', tfc)
                        if a != True:
                            tfc = input('> ')
                    except Exception as e:
                        print(f"Steamauth | {e} ")
                        tfc = input('> ')
                    inp = _driver_steam.find_element_by_id('twofactorcode_entry')
                    btn = _driver_steam.find_element_by_id('login_twofactorauth_buttonset_entercode')
                    btn = btn.find_element_by_class_name('auth_button.leftbtn')
                    inp.send_keys(tfc)
                    btn.click()
                    _driver_steam.implicitly_wait(2)
                    if CheckTwofactorauthMessage():
                        break

            elif _driver_steam.find_element_by_id('login_twofactorauth_message_incorrectcode').is_displayed():
                time.sleep(3)
                print(f"Steamauth | Вы ввели неправильный код, попробуйте ещё раз | {_login}")
                print(f"Steamauth | Введите Steam Guard код | {_login})")
                try:
                    mafiles = os.listdir('mafiles')
                    for mafile in mafiles:
                        with open(f'mafiles/{mafile}', 'r') as f:
                            json_mafile = json.load(f)
                            cur_login = json_mafile['account_name']
                            if _login == cur_login:
                                shared = json_mafile['shared_secret']
                                tfc = self.getcode(shared)
                                print('>', tfc)
                except:
                    tfc = input('> ')
                if self.is_element_present(_driver_steam, By.ID, 'login_twofactorauth_buttonset_incorrectcode'):
                    btn = _driver_steam.find_element_by_id('login_twofactorauth_buttonset_incorrectcode')
                    btn = btn.find_element_by_class_name('auth_button.leftbtn')
                    inp.send_keys(tfc)
                    btn.click()
                    _driver_steam.implicitly_wait(2)
                    if CheckTwofactorauthMessage():
                        break

            elif _driver_steam.find_element_by_id('captcha_entry').is_displayed() and _driver_steam.find_element_by_id(
                    'error_display').is_displayed():
                if self.is_element_present(_driver_steam, By.ID, 'captchaImg'):
                    imgurl = _driver_steam.find_element_by_id('captchaImg').get_attribute('src')
                    urllib.request.urlretrieve(imgurl, "captcha.png")
                    time.sleep(2)
                    img = Image.open("captcha.png")  # Открытие изображения желательно проводить в интерфейсе
                    print(f"Steamauth | Введите текст с изображения | {_login}")
                    img.show()
                    captcha = input('> ')
                    try:
                        os.remove("captcha.png")
                    except:
                        pass
                    _driver_steam.find_element_by_id('input_captcha').send_keys(captcha)
                    _driver_steam.find_element_by_class_name('btn_green_white_innerfade').click()
                    _driver_steam.implicitly_wait(2)
                    if CheckTwofactorauthMessage():
                        break

            elif _driver_steam.find_element_by_id('error_display').is_displayed():
                print(
                    f"Steamauth | За последнее время в вашей сети произошло слишком много безуспешных попыток входа.\n "
                    f"Пожалуйста, подождите и повторите попытку позже. (Change ip) | {_login}")
                exit()

        return True

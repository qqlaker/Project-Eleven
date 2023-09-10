import json
import os
import time
import pathlib
import zipfile
import selenium.webdriver.support.expected_conditions as EC
import undetected_chromedriver as undchromedriver

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

    def getcode(self, share):
        shared_secret = share
        one_time_authentication_code = generate_one_time_code(shared_secret)
        return one_time_authentication_code

    def login(self, driver_steam, login, password):
        while True:
            if self.is_element_present(driver_steam, By.CLASS_NAME, "newlogindialog_SegmentedCharacterInput_1kJ6q"):
                break
            elif self.is_element_present(driver_steam, By.CLASS_NAME, "newlogindialog_TextInput_2eKVn"):
                inputs = driver_steam.find_elements_by_class_name("newlogindialog_TextInput_2eKVn")
                login_input, password_input = inputs[0], inputs[1]
                login_input.send_keys(login)
                password_input.send_keys(password)
                driver_steam.find_element_by_class_name("newlogindialog_SubmitButton_2QgFE").click()
            elif self.is_element_present(driver_steam, By.CLASS_NAME, "newlogindialog_TextInput_2eKVn.newlogindialog_Danger_1-HwJ"):
                print(f"Steamauth | Неверный логин или пароль | {login}")
                return False
            else:
                print(f"Steamauth | Неизвестная ошибка | {login}")
                return False

        a = False
        while a == False:
            print(driver_steam.current_url)
            if self.is_element_present(driver_steam, By.CLASS_NAME, "newlogindialog_SegmentedCharacterInput_1kJ6q"):
                if self.is_element_present(driver_steam, By.CLASS_NAME, "newlogindialog_SegmentedCharacterInput_1kJ6q.newlogindialog_Danger_1-HwJ"):
                    print(f"Steamauth | Неверный код, попробуйте ещё раз | {login}")
                twoFactInp = driver_steam.find_element_by_class_name("newlogindialog_SegmentedCharacterInput_1kJ6q").find_elements_by_tag_name("input")[0]
                print(f'Введите Steam Guard код для {login}')
                mafiles = os.listdir('../mafiles')
                for mafile in mafiles:
                    with open(f'mafiles/{mafile}', 'r') as f:
                        json_mafile = json.load(f)
                        cur_login = json_mafile['account_name']
                        if login == cur_login:
                            shared = json_mafile['shared_secret']
                            tfc = self.getcode(shared)
                            print('>', tfc)
                        else:
                            tfc = input('> ')
                            if len(tfc) != 5:
                                print(f"Steamauth | Неверный код, попробуйте ещё раз | {login}")
                twoFactInp.send_keys(tfc)
                check = 0
                while self.is_element_present(driver_steam, By.CLASS_NAME, "throbber_roundFill_2FWWt") and check < 20:
                    time.sleep(1)
                    check += 1
            elif self.is_element_present(driver_steam, By.CLASS_NAME, "newlogindialog_FailureDescription_3gFes"):
                print(f"Steamauth | При входе в аккаунт произошла ошибка. Повторите попытку позже. | {login}")
                return False
            elif "steamcommunity.com/login/home" not in driver_steam.current_url:
                a = True
            else:
                print(f"Steamauth | Неудачная авторизация | {login}")
                return False
        print(f"Steamauth | Успешная авторизация | {login}")
        return True
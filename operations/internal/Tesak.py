from selenium.common.exceptions import NoSuchElementException
from func_timeout import func_timeout, FunctionTimedOut
from selenium.webdriver.common.by import By
from os.path import isfile, join
from service.Steamauth import Steamauth
from service.Runurl import Runurl
from os import listdir

import time


class Tesak(Steamauth):

    def __init__(self, logins):
        self.logins = logins

    def change_logins(self, logins):
        self.logins = logins

    def betting_csgorun(self, bet_driver, account):

        def bet(driver):
            attempts = 0
            while True:
                inventory_items = driver.find_element_by_class_name('grid.place-content-start')
                inventory_items.find_elements_by_tag_name('button')[0].click()
                driver.find_elements_by_class_name('btn-base.px-7')[0].click()
                driver.find_element_by_class_name('btn.btn--blue.h-55').click()
                time.sleep(0.5)
                try:
                    info = driver.find_element_by_class_name('notification.notification--info')
                    if 'Вы успешно поставили на сумму' in info.text:
                        return True
                except NoSuchElementException:
                    attempts += 1
                    if attempts >= 5:
                        return False

        def buy_item(deposit, driver):
            deposit = str(deposit)

            def exchange():
                change_btn = driver.find_element_by_class_name('btn.btn--green')
                change_btn.click()
                time.sleep(1)
                inp = driver.find_element_by_id('exchange-filter-maxPrice-field')
                inp.send_keys(deposit)
                time.sleep(2)
                withdraw_list = driver.find_element_by_class_name('grid.grow.place-content-start')
                time.sleep(2)
                withdraw_list.find_elements_by_class_name('btn-base.drop-preview')[-1].click()
                time.sleep(2)
                driver.find_element_by_class_name('btn.text-green-light').click()
                driver.refresh()
                time.sleep(2)
                driver.implicitly_wait(10)

            balance = float(driver.find_element_by_class_name('text-sm.text-orange').text.split(' ')[0])
            inventory_items = driver.find_element_by_class_name('grid.place-content-start')
            items = inventory_items.find_elements_by_tag_name('button')
            if len(items) == 0 and balance == 0:
                with open('../../temp/zero_balance.txt', 'a') as f:
                    f.write(f'{account[0]}\n')
                return False
            for item in items:
                time.sleep(0.2)
                item.click()
            time.sleep(1)
            exchange()
            return True

        def bet_after_login():
            while True:
                try:
                    bet_driver.find_element_by_class_name('graph-svg.finish')
                    time.sleep(6)
                    if not bet(bet_driver):
                        with open('../../temp/unbetted_run.txt', 'a') as f:
                            f.write(f'{account[0]}\n')
                    break

                except NoSuchElementException:
                    time.sleep(1)

        bet_driver.get(Runurl.RUNURL)
        bet_driver.implicitly_wait(10)
        if self.is_element_present(bet_driver, By.CLASS_NAME, 'switcher__content'):
            switcher = bet_driver.find_element_by_class_name("switcher__content")
            switcher.click()
        bet_driver.find_element_by_class_name('btn.btn--green.steam-login').click()
        bet_driver.implicitly_wait(10)
        r = Steamauth.login(self, bet_driver, account[0], account[1])
        if r:
            inventory_items = bet_driver.find_element_by_class_name('grid.place-content-start')
            els = inventory_items.find_elements_by_tag_name('button')
            if len(els) == 1:
                if float(bet_driver.find_element_by_class_name('drop-preview__price').text.split(' ')[0]) > 0.25:
                    buy_item(0.2, bet_driver)
                bet_after_login()
            else:
                if buy_item(0.2, bet_driver):
                    bet_after_login()

        return account

    def bet_run(self):

        onlyfiles = [f for f in listdir("../../temp") if isfile(join("../../temp", f))]
        if not ('betted_run.txt' in onlyfiles):
            with open('../../temp/betted_run.txt', 'w+') as F:
                pass

        if not ('zero_balance.txt' in onlyfiles):
            with open('../../temp/zero_balance.txt', 'w+') as F:
                pass

        if not ('unbetted_run.txt' in onlyfiles):
            with open('../../temp/unbetted_run.txt', 'w+') as F:
                pass

        logins_w = [self.logins[i][0] for i in range(len(self.logins))]
        with open('../../temp/betted_run.txt', 'r') as f:
            for line in f:
                line = line.strip('\n')
                if line in logins_w:
                    logins_w.remove(line)

        last_logins_w = []
        while len(logins_w) != 0:
            print(logins_w)
            if logins_w != last_logins_w:
                last_logins_w = logins_w
                with open('../../temp/betted_run.txt', 'r+') as F:
                    for line in F:
                        if self.logins[0][0] == line.strip("\n"):
                            continue
                print("logins_w[0]:", logins_w[0])
                bet_driver = self.driverinit(proxy_for_login=logins_w[0])
                try:
                    if func_timeout(120, self.betting_csgorun, args=(bet_driver, self.logins[0],)):
                        print(logins_w)
                        with open('../../temp/betted_run.txt', 'a') as f:
                            f.write(f"{self.logins[0][0]}\n")
                        logins_w.remove(self.logins[0][0])
                    input("Close...")
                    bet_driver.quit()
                except FunctionTimedOut:
                    bet_driver.quit()
                except Exception as e:
                    print(e)
                    bet_driver.quit()
            else:
                break

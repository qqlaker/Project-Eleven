import time

from selenium.webdriver.common.by import By
from service.Steamauth import Steamauth
from service.Runurl import Runurl

# СДА
# Смена ника
# Пополнение
# Тесак

class AccsSetup(Steamauth):

    def alone(self):
        logins = []
        with open("config/accs.txt", "r") as f:
            for line in f:
                logins.append(line.split(" "))
        logins = [logins[40]]
        for _ in range(len(logins)):
            print(logins[_][0])
            # if _ < 150:
            #     continue
            driver = self.driverinit(Runurl.RUNURL, proxy_for_login=logins[_][0])
            driver.implicitly_wait(10)
            if self.is_element_present(driver, By.CLASS_NAME, 'switcher__content'):
                switcher = driver.find_element_by_class_name("switcher__content")
                switcher.click()
            driver.find_element_by_class_name('btn.btn--green.steam-login').click()
            driver.implicitly_wait(10)
            Steamauth.login(self, driver, logins[_][0], logins[_][1])
            driver.implicitly_wait(15)

            driver.find_element_by_class_name("header-user__photo").click()
            a = driver.find_element_by_xpath("/html/body/div/div[1]/div[2]/div[1]/div[2]/ul/li[3]/button")
            time.sleep(1)
            a.click()
            link_to_trade = driver.find_element_by_class_name("btn.btn--tiny.btn--green-light-ghost.normal-case."
                                                          "ml-auto.gap-12").get_attribute("href")
            driver.get(link_to_trade)
            driver.implicitly_wait(15)
            # https://steamcommunity.com/profiles/76561199166549877/tradeoffers/privacy
            # https://steamcommunity.com/profiles/{account_id}/
            account_id = link_to_trade[36:].split("/")[0]
            trade_url = driver.find_element_by_id("trade_offer_access_url").get_attribute("value")
            driver.execute_script("window.history.go(-1)")
            driver.implicitly_wait(10)
            driver.find_element_by_xpath("/html/body/div/div[1]/div[2]/div[1]/div[2]/ul/li[3]/button").click()
            a = driver.find_element_by_xpath("/html/body/div/div[1]/div[2]/div[1]/div[2]/div/div[2]/div/div[3]/input")
            a.clear()
            a.send_keys(trade_url)
            driver.find_element_by_class_name("btn.btn--green.btn--lg").click()
            driver.get(f"https://steamcommunity.com/profiles/{account_id}/edit/info")
            driver.implicitly_wait(15)

            inp = driver.find_elements_by_name("personaName")[-1]
            inp_value = str(inp.get_attribute("value"))
            inp.clear()
            inp.send_keys(inp_value + " run")
            driver.find_element_by_class_name("DialogButton._DialogLayout.Primary.Focusable").click()
            time.sleep(3)

            driver.get(Runurl.RUNURL)
            driver.find_element_by_xpath("/html/body/div[1]/div[1]/header/div[2]/div/button[1]").click()
            driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div[2]/div/div[1]/div[4]/ul/li[5]/button").click()
            driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div[2]/div/div[1]/div[5]/div/ul/li[4]/button").click()
            inp = driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/div/label[1]/input")
            inp.clear()
            inp.send_keys("0.25")
            driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div[2]/div/div[1]/div[5]/div/div[2]/button").click()

            input("Enter - переход к след аккаунту ...")
            with open("temp/betted_run.txt", "a+") as f:
                f.write(f"{logins[_][0]}\n")
            driver.close()
            driver.quit()

            # yayaya.tytytyty@mail.ru
            # pro.sto.z

            # TODO: bivfzfrqghye чекнуть заново

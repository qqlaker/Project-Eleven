import itertools
import queue
import threading
import os

from operations.internal.GetCookies import GetCookies
from operations.internal.Tesak import Tesak
from operations.external.GetPromo import GetPromo
from operations.internal.ActivRun import ActiveRun
from os import listdir
from os.path import isfile, join


# Statuses:

# GetCookies - получение куки
# Tesak - выполнение ставки на аккаунтах
# Mining_zero_unbet - обработка zero_balance.txt и unbetted_run.txt
# GetPromocode - парсинг промокода
# Activation - активация промокода
# GetCookies2 - дополнительное получение куки, если была ошибка на предыдущем этапе

# TODO: Нужно добавить проверку на наличие файлов и папок и их создание
class Csgorun:
    @staticmethod
    def main_branch():
        def set_status(status: str):
            print(status)
            with open("temp/status.txt", "w+") as F:
                F.write(status)

        set_status("GetCookies")
        onlyfiles = [f for f in listdir("temp") if isfile(join("temp", f))]
        if not ('status.txt' in onlyfiles):
            with open('temp/status.txt', 'w+') as F:
                pass

        if "cookies" not in os.listdir("temp"):
            os.mkdir("temp/cookies")

        # Читаем logins, сравниваем с логинами из proxy.txt ------------------------------
        logins = []
        with open('config/accs.txt', 'r') as accs:
            lines = accs.readlines()
            for line in lines:
                logins.append(line.strip('\n').split())
        logins.sort()
        logins = list(k for k, _ in itertools.groupby(logins))

        only_logins = [l[0] for l in logins]
        with open("config/proxy.txt", "r") as proxy_file:
            only_logins_proxy_file = [line.split(" ")[0] for line in proxy_file]
            for login in only_logins:
                assert login in only_logins_proxy_file  # прокси для данного аккаунта не задано

        # Проверяем и получаем cookies ---------------------------------------------------
        if GetCookies.check_date():  # по дате
            GetCookies(_logins=logins).main_rec()

        GetCookies(_logins=logins).main_rec(is_all=False)  # по наличию

        # Tesak по тем аккам, которых нет в betted_run.txt -------------------------------
        set_status("Tesak")
        logins_for_tesak = []
        bet_logins = []
        with open('temp/betted_run.txt', 'r+') as F:
            for _ in F:
                bet_logins.append(_.strip("\n"))
            for _ in range(len(logins)):
                if not ((f'{logins[_][0]}\n' in bet_logins) or (f'{logins[_][0]}' in bet_logins)):
                    logins_for_tesak.append([logins[_][0], logins[_][1]])
        print("logins_for_tesak:", logins_for_tesak)
        print("bet_logins:", bet_logins)
        Tesak(logins_for_tesak).bet_run()

        # Check and clear zero_balance.txt and unbetted_run.txt --------------------------
        set_status("Mining_zero_unbet")
        with open("temp/zero_balance.txt", "r+") as F:
            for _ in F:
                s = _.strip("\n")
                print(f'Zero balance: {s}')  # TODO: to tg

        with open("temp/unbetted_run.txt", "r+") as F:
            for _ in F:
                s = _.strip("\n")
                print(f'Not bet: {s}')  # TODO: to tg

        with open("temp/zero_balance.txt", 'w'):
            pass
        with open("temp/unbetted_run.txt", 'w'):
            pass

        # Get promo ----------------------------------------------------------------------
        set_status("GetPromocode")
        promo = GetPromo().run_vk()
        assert promo is not None

        # Activation ---------------------------------------------------------------------
        set_status("Activation")
        proxy = {}
        with open('config/proxy.txt', 'r') as F:
            for line in F:
                login, pro = line.split(" ")
                proxy[login] = pro

        bet_logins = []
        with open("temp/betted_run.txt", "r+") as F:
            for _ in F:
                bet_logins.append(_.strip("\n"))

        param_list = [[], [], []]
        for login in bet_logins:
            param_list[0].append(login)
            param_list[1].append(promo)
            param_list[2].append(proxy[login])

        q = queue.Queue()
        results = []
        threads = {}
        for _ in range(len(param_list[0])):
            threads[_] = threading.Thread(
                target=ActiveRun.activation, args=[param_list[0][_], param_list[1][_], q, param_list[2][_]])
            threads[_].start()

        for _ in range(len(threads)):
            response = q.get()
            results.append(response)
        for _ in range(len(threads)):
            threads[_].join()

        temp_param_list = []
        gc = False
        print('here')
        for f in results:
            print(f[1])
            if "Cannot read properties of undefined" in f[1] or "success" in f[1]:
                bet_logins.remove(f[0])
            elif "NOT_VERIFIED_CAPTCHA" in f[1]:
                temp_param_list.append([param_list[0][_], param_list[1][_], q, param_list[2][_]])
            elif ("NO COOKIE FILE" in f[1]) or ("Unauthorized" in f[1]):
                print("COOKIES UPDATE REQUIRED")
                gc = True
            elif "TESAK_DIDNT_KILL_HIMSELF" in f[1]:
                bet_logins.remove(f[0])
            else:
                print(f[1])

        print('here1')
        # Вторая попытка активации для тех, где капча не прошла
        results = []
        threads = {}
        print(q)
        while not q.empty():
            q.get()

        print("test1")
        print(temp_param_list)
        for params in temp_param_list:
            t = threading.Thread(target=ActiveRun.activation, args=params)
            t.start()

        print("test2")
        for _ in range(len(threads)):
            print("1")
            response = q.get()
            print("2")
            results.append(response)
            print("3")

        print("test3")
        print("threads:", threads)
        for _ in range(len(threads)):
            threads[_].join()

        print("test4")
        print("bet_logins:", bet_logins)
        print("results:", results)
        for f in results:
            if "Cannot read properties of undefined" in f[1] or "success" in f[1]:
                bet_logins.remove(f[0])
            else:
                print(f[1])

        print("test5")
        print("bet_logins1:", bet_logins)
        with open("temp/betted_run.txt", "w+") as F:
            for login in bet_logins:
                F.write(f"{login}\n")

        print('here3')
        # TODO: Отправляем ACTIV.txt в тг
        with open("temp/ACTIV.txt", "r+") as F:
            for _ in F:
                print(_.strip("\n"))
        with open("temp/ACTIV.txt", "w+") as F:
            pass

        set_status("GetCookies2")  # -----------------------------------------------------
        if gc:
            GetCookies(_logins=logins).main_rec()

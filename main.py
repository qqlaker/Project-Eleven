import itertools
import threading
import multiprocessing

from Csgorun import Csgorun


if __name__ == '__main__':

    process = multiprocessing.Process(target=Csgorun.main_branch())
    process.start()



    # - GetCookies test -
    # if GetCookies.check_date():
    #     GetCookies(_logins=logins).main_rec()

    # - GetPromo test -
    # promo = GetPromo().run_vk()
    # print(promo)

    # - tg messages -

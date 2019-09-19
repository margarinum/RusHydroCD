#!/usr/bin/python3.6
from Refresher import Refresher
from Checker import Checker
import threading
import time
import configparser
import API

config = configparser.ConfigParser()
config.read('config.ini')

CHECKERSPERIOD = config.getint('Contoller', 'CHECKERSPERIOD') * 60


def runRefresh():
    refresher = Refresher()
    refresher.NEEDPOST = True
    checker = Checker()
    checker.NEEDPOST = True
    while True:
        if refresher.checkLocalTagRegistry():
            refresher.deploy()
        checker.check()
        time.sleep(CHECKERSPERIOD)

def runApi():
    API.runApi()


def thr():
    refresherThread = threading.Thread(target=runRefresh)
    apiThread = threading.Thread(target=runApi)

    refresherThread.start()
    apiThread.start()

    refresherThread.join()
    apiThread.join()


if __name__ == '__main__':
    thr()

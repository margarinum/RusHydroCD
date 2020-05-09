#!/usr/bin/python3.6
from Refresher import Refresher
from Checker import Checker
import threading
import time
import configparser
import logging
import threading

config = configparser.ConfigParser()
config.read('config.ini')
UPDATERLOGFILE = config.get('Shared', 'LOGFILENAME')



class Runner():

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.CHECKERSPERIOD = config.getint('Controller', 'CHECKERSPERIOD') * 60
        self.AUTODELOY = False
        logging.basicConfig(filename=UPDATERLOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')
        self.status = False
        self.refresher = Refresher()


    def setStatus(self, status):
        self.status = status
        return self.status

    def getPeriod(self):
        return self.CHECKERSPERIOD

    def setPerion(self, period):
        self.CHECKERSPERIOD = period
        return self.CHECKERSPERIOD

    def run(self):
        logging.info("runner started")
        while self.status:
            self.runRefreshnChecker()
            logging.info("runner going to sleep")
            time.sleep(self.CHECKERSPERIOD)


    def runRefreshnChecker(self):
        #checker = Checker()
        #checker.NEEDPOST = True
        if self.refresher.checkLocalTagRegistry():
            self.refresher.deploy()

#   До лучших времен:
#    def runThreads(self):
#        refresherThread = threading.Thread(target=self.runRefreshnChecker)
#        refresherThread.start()
#        refresherThread.join()

#!/usr/bin/python3.6
import os
import time
import logging
from Refresher import Refresher
UPDATERFILENAME = 'Refresher.py'
CHECKERFILENAME = 'Checker.py'
MAILERFILENAME = 'Mailer.py'
SLEEPINTERVAL = 900
UPDATERLOGFILE = 'updater.log'


def setPermissions():
    os.system('chmod ugo+rx {}'.format(UPDATERFILENAME))
    os.system('chmod ugo+rx {}'.format(CHECKERFILENAME))
    os.system('chmod ugo+rx {}'.format(MAILERFILENAME))
    os.system('chmod ugo+rw {}'.format(UPDATERLOGFILE))


def startup():
    setPermissions()
    logging.basicConfig(filename=UPDATERLOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')
    logging.info('Autoupdater started')
    refresher = Refresher()
    refresher.NEEDPOST = True
    while True:
        if refresher.checkLocalTagRegistry():
            refresher.deploy()
        time.sleep(SLEEPINTERVAL)
        os.system('./{}'.format(CHECKERFILENAME))


if __name__ == '__main__':
    setPermissions()
    startup()

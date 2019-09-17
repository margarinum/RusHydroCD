#!/usr/bin/python3.6
from Refresher import Refresher
from Checker import Checker


def run():
    refresher = Refresher()
    if refresher.checkLocalTagRegistry():
        refresher.NEEDPOST = True
        refresher.deploy()


if __name__ == '__main__':
    run()

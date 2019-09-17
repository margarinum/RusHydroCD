#!/usr/bin/python3.6

import os
from Mailer import Mailer
import refreshTagEmail
import logging
import yaml
import configparser
from Refresher import Refresher

config = configparser.ConfigParser()
config.read('config.ini')

COMPOSERLOCATION = config.get('Shared', 'COMPOSEDIRECTORY')
COMPOSERFILE = config.get('Checker', 'COMPOSERFILE')
UPDATERLOGFILE = config.get('Shared', 'LOGFILENAME')

NEEDPOST = config.getboolean('Checker', 'NEEDPOST')
LASTCHANSE = True

recepients = ['margarinum@gmail.com']


class Checker:

    def __init__(self):

        self.recepients = recepients
        self.needPost = NEEDPOST
        self.lastChanse = True
        logging.basicConfig(filename=UPDATERLOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')

    # Парсим конфиг и забираем имя имеджей, которые доджны работать
    def getServicesYml(self):
        with open(os.path.join(COMPOSERLOCATION, COMPOSERFILE)) as f:
            data_map = yaml.safe_load(f)
            dct = dict(data_map['services'])
            return list(dct.keys())

    # Получаем обработанный массив работающих имеджей
    def getRunningImages(self):
        imagesList = []
        output = os.popen('docker ps -f status=running --format "{{.Names}}"').read()
        for item in output.split('\n'):
            if len(item) > 1:
                imagesList.append(str(item).replace('composer_', '').replace('_1', ''))
        return imagesList

    # Сравнимаем с эталоном
    def checkRunningImages(self):
        return list(set(self.getServicesYml()) - set(self.getRunningImages()))

    def lastChanse(self, obj):
        obj.composerStop()
        obj.composerStart()

    def post(self, badImages, obj):
        mailer = Mailer(mailType='alert', recepients=recepients, ip=obj.getIP(),
                        component=', '.join(badImages))
        mailer.generateMessage()
        mailer.send()

    # Отправляем письмо
    def checkNsend(self):
        badImages = self.checkRunningImages()
        if badImages:
            refresher = Refresher()
            if self.needPost:
                self.post(badImages, refresher)
            if LASTCHANSE:
                refresher.composerStop()
                refresher.composerStart()
                badImages = self.checkRunningImages()
                if badImages:
                    self.post(badImages, refresher)
            logging.info('Alert! {} is not working'.format(', '.join(badImages)))
        else:
            logging.info('Checker alive')

#!/usr/bin/python3.6

import os
from Mailer import Mailer
import logging
import yaml
import configparser
import datetime
from Refresher import Refresher

config = configparser.ConfigParser()
config.read('config.ini')

COMPOSERLOCATION = config.get('Shared', 'COMPOSEDIRECTORY')
COMPOSERFILE = config.get('Checker', 'COMPOSERFILE')
UPDATERLOGFILE = config.get('Shared', 'LOGFILENAME')
LOGDIRNAME = 'logs'

NEEDPOST = config.getboolean('Checker', 'NEEDPOST')
LASTCHANSE = True

recepients = ['margarinum@gmail.com']


class Checker:

    def __init__(self):

        self.recepients = recepients
        self.NEEDPOST = NEEDPOST
        self.lastChanse = True
        logging.basicConfig(filename=UPDATERLOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')

    # Парсим конфиг и забираем имя имеджей, которые доджны работать
    def getServicesYml(self):
        with open(os.path.join(COMPOSERLOCATION, COMPOSERFILE)) as f:
            data_map = yaml.safe_load(f)
            dct = dict(data_map['services'])
            return list(dct.keys())

    # Получаем обработанный массив работающих имеджей
    # def getRunningImages(self):
    #     imagesList = []
    #     output = os.popen('docker ps -f status=running --format "{{.Names}}"').read()
    #     for item in output.split('\n'):
    #         if len(item) > 1:
    #             imagesList.append(str(item).replace('composer_', '').replace('_1', ''))
    #     return imagesList

    def getRunningImages(self):
        imagesList = {}
        output = os.popen('docker ps -f status=running --format "{{.Names}}:{{.ID}}"').read()
        for item in output.split('\n'):
            if len(item) > 1:
                splitted = item.split(":")
                # print(splitted[0].replace('composer_', '').replace('_1', ''))
                imagesList[str(splitted[0].replace('composer_', '').replace('_1', ''))] = splitted[1]
                # print(item.split(":")[0].replace('composer_', '').replace('_1', ''))
                # imagesList.append(str(item).replace('composer_', '').replace('_1', ''))
        return imagesList

    def getInfoByID(self, id):
        command = ('docker ps -f id=%s --format "ID:{{.ID}},Name:{{.Names}},Status:{{.Status}},' +
                   'Size:{{.Size}},Created:{{.CreatedAt}},Running for:{{.RunningFor}}"')
        imagesList = {}
        output = os.popen(
            command % id).read().replace('\n', '')
        print(output)
        for item in output.split(','):
            if len(item) > 1:
                splitted = item.split(":")
                imagesList[splitted[0]] = splitted[1]
        return imagesList

    # Сравнимаем с эталоном
    def checkRunningImages(self):
        return list(set(self.getServicesYml()) - set(self.getRunningImages().keys()))

    def getIdByName(self, name):
        return self.getRunningImages()[name]

    def getLogs(self, imageID):
        fileName = imageID + ":" + (
            datetime.datetime.strftime(datetime.datetime.today(), "%d%m%Y-%H%M%S")) + '.log'
        path = os.path.join(os.getcwd(), LOGDIRNAME)
        os.system('cd {pathToDir};docker logs {id} > {filename}'.format(pathToDir=path, id=imageID, filename=fileName))
        return os.path.join(os.getcwd(), LOGDIRNAME, fileName)

    def deleteLogFile(self, path):
        os.system('rm -rf {pathToFile}'.format(pathToFile=path))

    def lastChanse(self, obj):
        obj.composerStop()
        obj.composerStart()

    def post(self, badImages, obj):
        mailer = Mailer(mailType='alert', recepients=recepients, ip=obj.getIP(),
                        component=', '.join(badImages))
        mailer.generateMessage()
        mailer.send()

    # Отправляем письмо
    def check(self):
        badImages = self.checkRunningImages()
        if badImages:
            refresher = Refresher()
            if self.NEEDPOST:
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

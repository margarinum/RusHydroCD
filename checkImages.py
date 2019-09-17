#!/usr/bin/python3.6

import os
from Mailer import Mailer
import refreshTagEmail
import logging
import yaml

COMPOSEFILE = 'docker-compose.yml'

recepients = ['margarinum@gmail.com']


# Парсим конфиг и забираем имя имеджей, которые доджны работать
def getServicesYml():
    with open(COMPOSEFILE) as f:
        data_map = yaml.safe_load(f)
        dct = dict(data_map['services'])
        return list(dct.keys())


# Получаем обработанный массив работающих имеджей
def getRunningImages():
    imagesList = []
    output = os.popen('docker ps -f status=running --format "{{.Names}}"').read()
    for item in output.split('\n'):
        if len(item) > 1:
            imagesList.append(str(item).replace('composer_', '').replace('_1', ''))
    return imagesList


# Сравнимаем с эталоном
def checkRunningImages():
    return list(set(getServicesYml()) - set(getRunningImages()))


# Отправляем письмо
def checkNsend():
    badImages = checkRunningImages()
    if badImages:
        mailer = Mailer(mailType='alert', recepients=recepients, ip=refreshTagEmail.getIP(),
                        component=', '.join(badImages))
        mailer.generateMessage()
        mailer.send()
        logging.info('Alert! {} is not working'.format(', '.join(badImages)))
    else:
        logging.info('Checker alive')


def main():
    checkNsend()


if __name__ == '__main__':
    logging.basicConfig(filename='updater.log', level=logging.INFO, format='%(asctime)s %(message)s')
    main()

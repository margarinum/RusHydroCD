#!/usr/bin/python3.6

import os
import requests
import fileinput
import time
import logging
import platform
import subprocess
import re
import socket

from Mailer import Mailer

recipientsWarning = ["margarinum@gmail.com"]
recipientsUpdate = ["margarinum@gmail.com"]

# Registry
REG_USERNAME = 'egais'
REG_PASSWORD = '9ZnXxVFlPnQkDSq'
REGISTRY = 'https://docreg.taskdata.work'
COMPOSEENVFILE = '.env'
# Включение отправки оповещения
NEEDPOST = True
# Включение задержки между предупреждением и обновлением
DELAY = False
DELAYTOUPDATE = 300
DEPLOYONLYMASTERBACKEND = False
BACKENDMASTERBRANCH = 'master'


repos = ['rushydro-portal', 'rushydro-webclient']
confType = {'rushydro-portal': 'BACKEND_TAG', 'rushydro-webclient': 'WEBCLIENT_TAG'}


# Возвращает последний элемент справочника
def getLastItemDict(dictIn):
    return dictIn[int(sorted(dictIn.keys())[-1])]


# Управление Composer
def composerController(command):
    print(os.system('./{}'.format(command)))


# Забрать все теги из репозитория
def getAllTagsRegistry(repo, reg=REGISTRY):
    queryString = str('{}/v2/{}/tags/list'.format(reg, repo))
    tagsList = requests.get(queryString, auth=(REG_USERNAME, REG_PASSWORD)).json()["tags"]
    tagsDict = {i: tagsList[i] for i in range(len(tagsList))}
    return tagsDict


# Забрать последний тег из репозитория
def getLastTagRegistry(repo):
    allCommits = getAllTagsRegistry(repo)
    if DEPLOYONLYMASTERBACKEND and repo == repos[0]:
        masterBackendCommits = {}
        for item in allCommits.keys():
            if 'master' in allCommits[item]:
                masterBackendCommits[item] = allCommits[item]
        return getLastItemDict(masterBackendCommits)
    return getLastItemDict(allCommits)


# Забрать конфигурационную строку из .env
def getConfEnvFile(repo):
    with open(os.path.join(os.getcwd(), COMPOSEENVFILE)) as envFile:
        for line in envFile:
            allConfString = list(re.findall(r'{}=\S+$'.format(confType[repo]), line))
            if len(allConfString)>0:
                return allConfString[0]


# Проверить разницу между последним тегом и тем, который в конфигурационном файле
def getDiff(repo):
    lastTagRegistry = getLastTagRegistry(repo)
    confLine = getConfEnvFile(repo)
    confTag = str(confLine).replace(confType[repo]+'=', '')
    if lastTagRegistry != confTag:
        return {"last": lastTagRegistry, "old": confTag}
    else:
        return False


# Изменение конфигурационного файла
def editConf(repo, tag):
    confString = str(getConfEnvFile(repo))
    newConfString = confString.replace(tag['old'], tag['last'])
    for line in fileinput.input(os.path.join(os.getcwd(), COMPOSEENVFILE), inplace=1, backup='.bak'):
        print(line.replace(confString, newConfString), end='')


# Поиск IP машины
def getIP():
    intDict = {}
    os = platform.system()
    if os == 'Windows':
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        return ip

    elif os == 'Linux':
        command = r"""ip -o -4 addr show | awk '{print "" $2": "$4}'"""
        ips = subprocess.check_output([command], shell=True).decode('utf-8')
        ips = list(ips.split('\n'))

        for line in ips:
            if len(line) > 1:
                arr = line.split(': ')
                intDict[arr[0]] = re.sub(r'/[0-9]{2}', '', arr[1])
        ip = intDict['wlp4s0']
    return ip


# Отправка письма
def sendMail(repo, tag, ip):
    if DELAY:
        warningMsg = Mailer('warn', recipientsWarning, repo = repo, tag = tag, ip = ip)
        warningMsg.generateMessage()
        warningMsg.send()
        time.sleep(DELAYTOUPDATE)
    updateMsg = Mailer('upd', recipientsUpdate, repo = repo, tag = tag, ip = ip)
    updateMsg.generateMessage()
    updateMsg.send()


# Основная функция
def checkUpdates():
    for repo in repos:
        diff = getDiff(repo)
        if diff:
            composerController('stop')
            editConf(repo, diff)
            logging.info('{} updates to {}'.format(repo, diff["last"]))
            composerController('start')
            if NEEDPOST:
                sendMail(repo, diff["last"], getIP())

        else:
            logging.info('Updater alive')
            print('nothing to update')


def main():
    checkUpdates()


if __name__ == '__main__':
    logging.basicConfig(filename='updater.log', level=logging.INFO, format='%(asctime)s %(message)s')
    main()

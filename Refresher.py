#!/usr/bin/python3.6

import os
import requests
import fileinput
import logging
import platform
import subprocess
import re
import socket
import configparser

from Mailer import Mailer

config = configparser.ConfigParser()
config.read('config.ini')

# Registry
REGISTRY = config.get('Refresher', 'REGISTRY')
COMPOSEENVFILE = config.get('Shared', 'COMPOSEENVFILE')
REG_USERNAME = config.get('Refresher', 'REG_USERNAME')
REG_PASSWORD = config.get('Refresher', 'REG_PASSWORD')
# Local
UPDATERLOGFILE = config.get('Shared', 'LOGFILENAME')
COMPOSERLOCATION = config.get('Shared', 'COMPOSEDIRECTORY')
CONFTYPEBACKEND = config.get('Refresher', 'CONFTYPEBACKEND')
CONFTYPEFRONTEND = config.get('Refresher', 'CONFTYPEFRONTEND')
BACKENDREPO = config.get('Refresher', 'BACKENDREPO')
FRONTENDREPO = config.get('Refresher', 'FRONTENDREPO')

INTERFACE = 'wlp4s0'


class Refresher:

    def __init__(self):
        self.repos = {BACKENDREPO: CONFTYPEBACKEND, FRONTENDREPO: CONFTYPEFRONTEND}
        self.currentTags = self.getCurrentTags()
        self.DEPLOYONLYMASTERBACKEND = False
        self.NEEDPOST = False
        logging.basicConfig(filename=UPDATERLOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')
        logging.info('Deployer started')

    # Возвращает последний элемент справочника
    def getLastItemDict(self, dictIn):
        return dictIn[int(sorted(dictIn.keys())[-1])]

    # Управление Composer
    def composerStop(self):
        os.system('cd {}; ./{}'.format(COMPOSERLOCATION, 'stop'))

    def composerStart(self):
        os.system('cd {}; ./{}'.format(COMPOSERLOCATION, 'start'))

    # Получаем обработанный массив работающих имеджей
    def getRunningImages(self):
        imagesList = []
        output = os.popen('docker ps -f status=running --format "{{.Names}}"').read()
        for item in output.split('\n'):
            if len(item) > 1:
                imagesList.append(str(item).replace('composer_', '').replace('_1', ''))
        return imagesList

    def getStateCompose(self):
        if len(self.getRunningImages()) > 0:
            return True
        else:
            return False

    # Забрать все теги из репозитория
    def getAllTagsRegistry(self, repo, reg=REGISTRY):
        queryString = str('{}/v2/{}/tags/list'.format(reg, repo))
        tagsList = requests.get(queryString, auth=(REG_USERNAME, REG_PASSWORD)).json()["tags"]
        tagsDict = {i: tagsList[i] for i in range(len(tagsList))}
        return tagsDict

    # Забрать последний тег из репозитория
    def getLastTagRegistry(self, repo):
        allCommits = self.getAllTagsRegistry(repo)
        if self.DEPLOYONLYMASTERBACKEND and repo == BACKENDREPO:
            masterBackendCommits = {}
            for item in allCommits.keys():
                if 'master' in allCommits[item]:
                    masterBackendCommits[item] = allCommits[item]
            return self.getLastItemDict(masterBackendCommits)
        return self.getLastItemDict(allCommits)

    def checkLocalTagRegistry(self):
        checked = {}
        self.currentTags = self.getCurrentTags()
        for i in self.repos.keys():
            if self.currentTags[i] != self.getLastTagRegistry(i):
                checked[i] = self.getLastTagRegistry(i)
            else:
                logging.info('{}: no new tags found'.format(i))
        return checked

    def sendMail(self, type, repo, tag):
        mailer = Mailer(type, repo=repo, tag=tag, ip=self.getIP())
        mailer.generateMessage()
        mailer.send()

    def deploy(self):
        self.currentTags = self.getCurrentTags()
        for i in self.repos.keys():
            if self.currentTags[i] != self.getLastTagRegistry(i):
                print(self.currentTags[i])
                print(self.getLastTagRegistry(i))
                if self.getStateCompose():
                    self.composerStop()
                lastTag = self.getLastTagRegistry(i)
                self.editConf(i, lastTag)
                self.currentTags = self.getCurrentTags()
                logging.info('{} updates to {}'.format(i, lastTag))
                if self.NEEDPOST:
                    self.sendMail('upd', i, lastTag)
        return self.currentTags

    # Забрать конфигурационную строку из .env
    def getConfEnvFile(self, repo):
        with open(os.path.join(COMPOSERLOCATION, COMPOSEENVFILE)) as envFile:
            for line in envFile:
                allConfString = re.match(r'{}=\S+$'.format(self.repos[repo]), line)
                if allConfString:
                    return allConfString.group(0)

    def getTagFromString(self, repo):
        line = self.getConfEnvFile(repo)
        if type(line) == str:
            return line.replace(self.repos[repo] + '=', '')

    def getCurrentTags(self):
        dct = {}
        for rep in self.repos:
            dct[rep] = self.getTagFromString(rep)
        return dct

    # Изменение конфигурационного файла
    def editConf(self, repo, tag):
        confString = str(self.getConfEnvFile(repo))
        newConfString = confString.replace(str(self.getTagFromString(repo)), str(tag))
        for line in fileinput.input(os.path.join(COMPOSERLOCATION, COMPOSEENVFILE), inplace=1, backup='.bak'):
            print(line.replace(confString, newConfString), end='')

    # Поиск IP машины
    def getIP(self):
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
            ip = intDict[INTERFACE]
        return ip

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

# Доделать

# Registry
REGISTRY = 'https://docreg.taskdata.work'
COMPOSEENVFILE = '.env'
REG_USERNAME = config.get('Refresher', 'REG_USERNAME')
REG_PASSWORD = config.get('Refresher', 'REG_PASSWORD')

CONFTYPEBACKEND = config.get('Refresher', 'CONFTYPEBACKEND')
CONFTYPEFRONTEND = config.get('Refresher', 'CONFTYPEFRONTEND')
BACKENDREPO = config.get('Refresher', 'BACKENDREPO')
FRONTENDREPO = config.get('Refresher', 'FRONTENDREPO')

# Включение задержки между предупреждением и обновлением
INTERFACE = 'wlp4s0'


class Refresher:

    def __init__(self):
        self.repos = {BACKENDREPO: CONFTYPEBACKEND, FRONTENDREPO: CONFTYPEFRONTEND}
        self.lastCheckedTags = {BACKENDREPO: self.getTagFromString(CONFTYPEBACKEND),
                                FRONTENDREPO: self.getTagFromString(CONFTYPEFRONTEND)}
        self.currentTags = self.getCurrentTags()
        self.NEEDPOST = True
        self.DEPLOYONLYMASTERBACKEND = False

        self.NEEDPOST = False

        logging.basicConfig(filename='updater.log', level=logging.INFO, format='%(asctime)s %(message)s')

    # Возвращает последний элемент справочника
    def getLastItemDict(self, dictIn):
        return dictIn[int(sorted(dictIn.keys())[-1])]

    # Управление Composer
    def composerController(self, command):
        print(os.system('./{}'.format(command)))

    # Забрать все теги из репозитория
    def getAllTagsRegistry(self, repo, reg=REGISTRY):
        queryString = str('{}/v2/{}/tags/list'.format(reg, repo))
        tagsList = requests.get(queryString, auth=(REG_USERNAME, REG_PASSWORD)).json()["tags"]
        tagsDict = {i: tagsList[i] for i in range(len(tagsList))}
        return tagsDict

    # Забрать последний тег из репозитория
    def getLastTagRegistry(self, repo):
        allCommits = self.getAllTagsRegistry(repo)
        if self.DEPLOYONLYMASTERBACKEND and repo == self.repos[0]:
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
        return checked

    def sendMail(self, type, repo, tag):
        mailer = Mailer(type, repo=repo, tag=tag, ip=self.getIP())
        mailer.generateMessage()
        mailer.send()

    def deploy(self):
        self.currentTags = self.getCurrentTags()
        for i in self.repos.keys():
            if self.currentTags[i] != self.getLastTagRegistry(i):
                lastTag = self.getLastTagRegistry(i)
                self.editConf(i, lastTag)
                self.composerController('start')
                self.currentTags = self.getCurrentTags()
                logging.info('{} updates to {}'.format(i, lastTag))
                if self.NEEDPOST:
                    self.sendMail('upd', i, lastTag)
        return self.currentTags


    # Забрать конфигурационную строку из .env
    def getConfEnvFile(self, repo):
        with open(os.path.join(os.getcwd(), COMPOSEENVFILE)) as envFile:
            for line in envFile:
                allConfString = list(re.findall(r'{}=\S+$'.format(repo), line))
                if len(allConfString) > 0:
                    return allConfString[0]

    def getTagFromString(self, repo):
        with open(os.path.join(os.getcwd(), COMPOSEENVFILE)) as envFile:
            for line in envFile:
                allConfString = list(re.findall(r'{}=\S+$'.format(repo), line))
                if len(allConfString) > 0:
                    return str(allConfString[0]).replace(repo + '=', '')


    def getCurrentTags(self):
        dct = {}
        for rep in self.repos:
            dct[rep] = self.getTagFromString(self.repos[rep])
        return dct

    # Изменение конфигурационного файла
    def editConf(self, repo, tag):
        confString = str(self.getConfEnvFile(self.repos[repo]))
        newConfString = confString.replace(self.getTagFromString(self.repos[repo]), tag)
        for line in fileinput.input(os.path.join(os.getcwd(), COMPOSEENVFILE), inplace=1, backup='.bak'):
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



#!/usr/bin/python3.6
import configparser
from behave.__main__ import main as behave_main
import os
import json
from datetime import datetime

config = configparser.ConfigParser()
config.read('behave.ini')
directoryTests = 'autotesting'
directoryReports = 'reports'


class Test:

    def __init__(self):
        self.storeReportStatus = True
        self.allTests = self.getAllTests()

    def setStoreReports(self, status):
        self.storeReportStatus = status
        return self.storeReportStatus

    def parseScenario(self, fileName):
        file = os.path.join(os.getcwd(), directoryTests, fileName)
        with open(file) as f_in:
            lines = list(line + '; \n' for line in (l.strip() for l in f_in) if line)
        return ''.join(lines)

    def getAllTests(self):
        tests = {}
        pathTests = os.path.join(os.getcwd(), directoryTests)
        for f in os.listdir(pathTests):
            if os.path.isfile(os.path.join(pathTests, f)) and '.feature' in f:
                tests[f] = self.parseScenario(f)

        return tests

    def runTests(self, testList):
        report = {}
        for test in testList:
            filename = test + datetime.strftime(datetime.now(), "%d%m%y%H:%M:%S")
            path = "{dir}/{testName}".format(testName=filename,
                                             dir=os.path.join(os.getcwd(), directoryTests,
                                                              directoryReports))
            behave_main(
                ["/home/dima/PycharmProjects/RusHydroCD/{dir}/{testName}".format(testName=test, dir=directoryTests),
                 "-f",
                 "json.pretty",
                 "-o",
                 "{dir}/{testName}".format(testName=filename,
                                           dir=os.path.join(os.getcwd(), directoryTests, directoryReports)), "-D",
                 "LOGIN={login}".format(login=config.get('behave', 'login')), "-D",
                 "PASSWORD={password}".format(password=config.get('behave', 'password'))
                 ])
            res = self.getReportFile(path)
            report[res[0]] = res[1]
            if not self.storeReportStatus:
                os.remove(path)
        return report

    def getReportFile(self, file):
        with open(file, 'r') as f:
            file = json.loads(f.read())[0]
            return [file['name'], file['status']]

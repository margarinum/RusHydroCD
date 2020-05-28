#!/usr/bin/python3.6
import configparser
from behave.__main__ import main as behave_main
import os
import json
from datetime import datetime

config = configparser.ConfigParser()
config.read('behave.ini')
directoryTests = config.get('behave', 'directoryTests')
directoryReports = config.get('behave', 'directoryReports')
directorySteps = config.get('behave', 'directorySteps')


class Test:

    def __init__(self):
        self.storeReportStatus = True
        self.allTests = self.getAllTests()

    def getAutotestsDir(self):
        return os.path.join(os.getcwd(), directoryTests)

    def getAutotestReportsDir(self):
        return os.path.join(self.getAutotestsDir(), directoryReports)

    def getAutotestStepsDir(self):
        return os.path.join(self.getAutotestsDir(), directorySteps)

    def setStoreReportsStatus(self, status):
        self.storeReportStatus = status
        return self.storeReportStatus

    def getStoreReportsStatus(self):
        return self.storeReportStatus

    def getPathTestFile(self, fileName):
        path = os.path.join(os.getcwd(), directoryTests,
                            fileName)
        if os.path.isfile(path):
            return path

    def getPathTestReport(self, fileName):
        return os.path.join(self.getAutotestReportsDir(), self.getLatestNameTestReport(fileName))

    def getLatestNameTestReport(self, fileName):
        dates = [f.replace(fileName, '') for f in os.listdir(self.getAutotestReportsDir()) if
                 os.path.isfile(os.path.join(self.getAutotestReportsDir(), f)) and fileName in f]
        dates.sort(reverse=True)
        return fileName + dates[0]

    def parseScenario(self, fileName):
        file = os.path.join(self.getAutotestsDir(), fileName)
        with open(file) as f_in:
            # lines = list(line + '; \n' for line in (l.strip() for l in f_in) if line)
            lines = list(line for line in (l for l in f_in) if line)
        return ''.join(lines)

    def getAllTests(self):
        tests = {}
        for f in os.listdir(self.getAutotestsDir()):
            if os.path.isfile(os.path.join(self.getAutotestsDir(), f)) and '.feature' in f:
                tests[f] = self.parseScenario(f)

        return tests

    def runTests(self, testList):
        report = []
        res = ''
        for test in testList:
            filename = test + datetime.strftime(datetime.now(), "%d%m%y%H:%M:%S")
            path = "{dir}/{testName}".format(testName=filename,
                                             dir=self.getAutotestReportsDir())
            behave_main(
                ["./{dir}/{testName}".format(testName=test, dir=directoryTests),
                 "-f",
                 "json.pretty",
                 "-o",
                 "{dir}/{testName}".format(testName=filename,
                                           dir=self.getAutotestReportsDir()), "-D",
                 "LOGIN={login}".format(login=config.get('behave', 'login')), "-D",
                 "PASSWORD={password}".format(password=config.get('behave', 'password'))
                 ])
            res = self.getReportFile(path)
            # report[res[0]] = res[1]
            if not self.storeReportStatus:
                os.remove(path)
            report.append(res)
        return report

    def uploadTest(self):
        pass

    def getReportFile(self, file):
        with open(file, 'r') as f:
            steps = {}
            file = json.loads(f.read())[0]
            for item in file['elements']:
                steps[item['name']] = item['status']
            return {file['name']: file['status'], 'Scenarios': steps}

#!/usr/bin/python3.6

from flask import Flask, jsonify, Response, request, send_file
from Refresher import Refresher
from Runner import Runner
from Checker import Checker
from Test import Test
import threading
import logging
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

runner = Runner()
runnerStatus = False
refresher = Refresher()
checker = Checker()
test = Test()

UPDATERLOGFILE = config.get('Shared', 'LOGFILENAME')
logging.basicConfig(filename=UPDATERLOGFILE, level=logging.INFO, format='%(asctime)s %(message)s')


def startAll():
    threadSimpleAPI = threading.Thread(target=runSimpleApi)

    threadSimpleAPI.daemon = True
    threadSimpleAPI.start()

    threadSimpleAPI.join()


def getCurrentTags():
    current = refresher.getCurrentTags()
    return jsonify({i: current[i] for i in current})


def checkNewTags():
    checked = refresher.checkLocalTagRegistry()
    if not checked:
        return jsonify({'Info': 'No updates available'})
    return jsonify({i: checked[i] for i in checked})


def update():
    refresher.NEEDPOST = False
    refresher.checkLocalTagRegistry()
    checked = refresher.deploy()
    return jsonify({i: checked[i] for i in checked})


def getAvailableTypes():
    refresher.NEEDPOST = True
    repos = refresher.repos
    return {key: repos[key] for key in repos.keys()}


def setCommits():
    tagTypes = getAvailableTypes()
    params = request.args
    for paramType in params:
        if paramType in tagTypes.keys():
            refresher.editConf(paramType, params[paramType])
    return getCurrentTags()


def startApp():
    refresher.composerStart()
    return getComposeState()


def stopApp():
    refresher.composerStop()
    return getComposeState()


def getComposeState():
    return jsonify({"Application running": refresher.getStateCompose()})


def getAllInfo():
    return jsonify({"Application running": refresher.getStateCompose(), "Autodeploy status": runner.status,
                    "Period (min)": int(runner.CHECKERSPERIOD / 60)})


def getAutoDeployStatus():
    return jsonify({"Autodeploy status": runner.status,
                    "Period (min)": int(runner.CHECKERSPERIOD / 60)})


def setAutoDeployStatus():
    global thread

    if request.args.get('set') == 'true':
        if runner.status:
            logging.info("AutoDeploy already True")
            return getAutoDeployStatus()

        runner.setStatus(True)
        thread = threading.Thread(target=runner.run, args=(), daemon=True)
        thread.start()
        logging.info('Autodeploy setted status: %s' % runner.status)
        return getAutoDeployStatus()
    if request.args.get('set') != 'true':
        if not runner.status:
            return getAutoDeployStatus()
        runner.setStatus(False)
        logging.info('Autodeploy setted status: %s' % runner.status)
        return getAutoDeployStatus()


def setAutoDeployPeriod():
    try:
        val = int(request.args.get('set'))
        runner.setPerion(val * 60)
        return getAutoDeployStatus()

    except ValueError:
        return jsonify({"Error": "Must be int!"})


def containers():
    return jsonify(checker.getRunningImages())


def containerInfo():
    containers = checker.getInfoByID(request.args.get('get'))
    if len(containers) > 0:
        return jsonify(containers)
    else:
        return jsonify({'Error': 'Container not started'})


def download():
    containerID = request.args.get('get')
    if containerID in list(checker.getRunningImages().values()):
        pathToLogs = checker.getLogs(containerID)
        logging.info('Saving file ' + pathToLogs)
        return send_file(pathToLogs, as_attachment=True)
    else:
        return jsonify({'Error': 'Container {ID} not started or not exists'.format(ID=containerID)})


def getAllTests():
    if len(list(test.getAllTests())) > 0:
        return jsonify(test.getAllTests())
    else:
        return jsonify({'Error': 'Autotests not found'})


def runAllTests():
    return jsonify(test.runTests(test.getAllTests()))


def runTest():
    testName = request.args.get('get')
    if testName in test.allTests:
        return jsonify(test.runTests([testName]))
    else:
        return jsonify({'Error': 'Autotest not found'})


def getTestInfo():
    testName = request.args.get('get')
    print(test.allTests)
    if testName in test.allTests:
        return jsonify(test.allTests[testName])
    else:
        return jsonify({'Error': 'Autotest not found'})


def getTasks():
    tasks = [
        {
            'id': '/api/v2.0/tasks/current',
            'type': u'get',
            'showTask': True,
            'title': u'Getting current deployed tags',
        },
        {
            'id': '/api/v2.0/tasks/check',
            'type': u'get',
            'showTask': True,
            'title': u'Checking repo new tags',
        },
        {
            'id': '/api/v2.0/tasks/startApp',
            'type': u'get',
            'showTask': True,
            'title': u'Starting compose',
        },
        {
            'id': '/api/v2.0/tasks/stopApp',
            'type': u'get',
            'showTask': True,
            'title': u'Stopping compose',
        },
        {
            'id': '/api/v2.0/tasks/AppStatus',
            'type': u'get',
            'showTask': True,
            'title': u'Getting compose status',
        },
        {
            'id': '/api/v2.0/tasks/AutoDeployStatus',
            'type': u'get',
            'showTask': True,
            'title': u'Getting autodeploy status',
        },
        {
            'id': '/api/v2.0/tasks/setAutoDeployStatus',
            'type': u'setBin',
            'showTask': True,
            'title': u'Setting auto deploy status, for example: /api/v2.0/tasks/setAutoDeployStatus?set=true',
        },
        {
            'id': '/api/v2.0/tasks/setAutoDeployPeriod',
            'type': u'setInt',
            'showTask': True,
            'title': u'Setting auto deploy period in minutes, for example: /api/v2.0/tasks/setAutoDeployPeriod?min=4',
        },
        {
            'id': '/api/v2.0/tasks/update',
            'type': u'get',
            'showTask': True,
            'title': u'Updating tags to latest from repo, restarting compose',
        },
        {
            'id': '/api/v2.0/tasks/containers',
            'type': u'getOpts',
            'showTask': True,
            'title': u'Get all running containers',
        },
        {
            'id': '/api/v2.0/tasks/containerInfo',
            'type': u'get',
            'showTask': False,
            'title': u'Get all running containers',
        },
        {
            'id': '/api/v2.0/tasks/download',
            'type': u'getFile',
            'showTask': False,
            'title': u'Getting logs from container, for example /api/v2.0/tasks/download?container=<idContainer>',
        },
        {
            'id': '/api/v2.0/tasks/autoTests',
            'type': u'getTests',
            'showTask': True,
            'title': u'Getting list of all autotests',
        },
        {
            'id': '/api/v2.0/tasks/runTest',
            'type': u'get',
            'showTask': False,
            'title': u'Run selected autotest',
        },
        {
            'id': '/api/v2.0/tasks/runAllTests',
            'type': u'get',
            'showTask': False,
            'title': u'Run all autotests',
        },
        {
            'id': '/api/v2.0/tasks/getTestInfo',
            'type': u'get',
            'showTask': False,
            'title': u'Getting autotest info',
        }
    ]

    return jsonify(tasks)


def runSimpleApi():
    app = Flask(__name__)  # create the Flask app

    @app.route('/api/v2.0/tasks')
    def getAllTasks():
        return getTasks()

    @app.route('/api/v2.0/')
    def heartbeat():
        return jsonify({'API online': True})

    @app.route('/api/v2.0/tasks/current')
    def getCurrTags():
        return getCurrentTags()

    @app.route('/api/v2.0/tasks/check')
    def checkTags():
        return checkNewTags()

    # @app.route('/api/v2.0/tasks/lastTags')
    # def upd():
    #     return update()

    # @app.route('/api/v2.0/tasks/setter')
    # def setterTask():
    #    return setCommits()

    @app.route('/api/v2.0/tasks/startApp')
    def startAppTask():
        return startApp()

    @app.route('/api/v2.0/tasks/stopApp')
    def stopTask():
        return stopApp()

    @app.route('/api/v2.0/tasks/AppStatus')
    def getStateAppTask():
        return getComposeState()

    @app.route('/api/v2.0/tasks/AutoDeployStatus')
    def autoDeployStatusTask():
        return getAutoDeployStatus()

    @app.route('/api/v2.0/tasks/setAutoDeployStatus')
    def setAutoDeployStatusTask():
        return setAutoDeployStatus()

    @app.route('/api/v2.0/tasks/setAutoDeployPeriod')
    def getAutoDeployPeriodTask():
        return setAutoDeployPeriod()

    @app.route('/api/v2.0/tasks/update')
    def updater():
        return update()

    @app.route('/api/v2.0/tasks/containers')
    def containersTask():
        return containers()

    @app.route('/api/v2.0/tasks/containerInfo')
    def containerInfoTask():
        return containerInfo()

    @app.route('/api/v2.0/tasks/download')
    def downloadTask():
        return download()

    @app.route('/api/v2.0/tasks/autoTests')
    def autoTestsTask():
        return getAllTests()

    @app.route('/api/v2.0/tasks/runAllTests')
    def runAllTestsTask():
        return runAllTests()

    @app.route('/api/v2.0/tasks/runTest')
    def runTestTask():
        return runTest()

    @app.route('/api/v2.0/tasks/getTestInfo')
    def getTestInfoTask():
        return getTestInfo()

    # Отправка команды не сохранять кэш
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = '0'
        response.headers["Pragma"] = "no-cache"
        return response

    app.run(host='0.0.0.0', debug=False, port=5000)


if __name__ == '__main__':
    startAll()

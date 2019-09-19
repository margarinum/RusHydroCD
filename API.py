#!/usr/bin/python3.6

from flask import Flask, jsonify, Response
from Refresher import Refresher

refresher = Refresher()

class EndpointAction(object):

    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        # self.action()
        return self.action()


class FlaskAppWrapper(object):
    app = None

    def __init__(self, name):
        self.app = Flask(name)

    def run(self):
        self.app.run(host='0.0.0.0')

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler))


def getTasks():
    tasks = [
        {
            'id': 'current',
            'title': u'Get current commits',
        },
        {
            'id': 'check',
            'title': u'Get current commits',
        },
        {
            'id': 'update',
            'title': u'Refresh to newest commits',
        }
    ]

    return jsonify({'tasks': tasks})


def getCurrentTags():
    current = refresher.getCurrentTags()
    return jsonify({i: current[i] for i in current})


def checkNewTags():
    checked = refresher.checkLocalTagRegistry()
    if not checked:
        return 'No updates available'
    return jsonify({i: checked[i] for i in checked})


def update():
    refresher.NEEDPOST = False
    refresher.checkLocalTagRegistry()
    checked = refresher.deploy()
    return jsonify({i: checked[i] for i in checked})


def runApi():

    a = FlaskAppWrapper('wrap')
    a.add_endpoint(endpoint='/api/v1.0/tasks', endpoint_name='tasks', handler=getTasks)
    a.add_endpoint(endpoint='/api/v1.0/tasks/current', endpoint_name='current', handler=getCurrentTags)
    a.add_endpoint(endpoint='/api/v1.0/tasks/check', endpoint_name='check', handler=checkNewTags)
    a.add_endpoint(endpoint='/api/v1.0/tasks/update', endpoint_name='update', handler=update)
    a.run()


if __name__ == '__main__':
    runApi()



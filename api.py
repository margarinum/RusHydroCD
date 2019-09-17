#!/usr/bin/python3.6

from flask import Flask, jsonify
from flask import abort
from Refresher import Refresher

app = Flask(__name__)

refresher = Refresher()

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
        'title': u'refresh to newest',
    }
]


@app.route('/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/api/v1.0/tasks/<string:task_id>', methods=['GET'])
def get_task(task_id):
    task = list(filter(lambda t: t['id'] == task_id, tasks))
    if len(task) == 0:
        abort(404)

    if (task[0]['id']) == 'current':
        current = refresher.getCurrentTags()
        return jsonify({i: current[i] for i in current})

    if (task[0]['id']) == 'check':
        checked = refresher.checkLocalTagRegistry()
        if not checked:
            return 'No updates available'
        return jsonify({i: checked[i] for i in checked})

    if (task[0]['id']) == 'update':
        refresher.NEEDPOST = False
        refresher.checkLocalTagRegistry()
        checked = refresher.deploy()
        return jsonify({i: checked[i] for i in checked})



if __name__ == '__main__':
    app.run(host='0.0.0.0')

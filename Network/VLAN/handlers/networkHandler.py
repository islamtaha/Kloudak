#!/usr/bin/python3.6
from lib import NetworkOps
from .tasks import networkNotificationTask

database = ''
broker = ''


def set_config(db, brkr):
    NetworkOps.database = db
    global database
    global broker
    database = db
    broker = brkr


def post(body):
    from lib.NetworkOps import network
    try:
        n = network(body['name'], body['owner'])
        n.create()
        body['status'] = 'success'
    except Exception as e:
        #log task
        print(e)
        body['status'] = 'failed'
    networkNotificationTask(broker, body)
    

def put():
    pass


def delete(body):
    from lib.NetworkOps import network
    try:
        n = network.get(body['name'], body['owner'])
        n.delete()
        body['status'] = 'success'
    except Exception as e:
        #log task
        print(e)
        body['status'] = 'failed'
    networkNotificationTask(broker, body)
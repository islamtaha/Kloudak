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

def put(body):
    pass


def delete(body):
    from lib.NetworkOps import Interface, network
    try:
        for net in body['networks']:
            n = network().get(name=net['network'], owner=body['owner'])
            iface = Interface().get(name=net['name'], network=n)
            iface.delete()
        body['status'] = 'success'
    except Exception as e:
        #log task
        print(e)
        body['status'] = 'failed'
    body['type'] = 'vm'
    networkNotificationTask(broker, body)



def post(body):
    from lib.NetworkOps import network
    print(body['networks'])
    try:
        for net in body['networks']:
            print(net)
            n = network(net['network'], body['owner'])
            n.addInterface(net['name'], net['host'], net['mac'])
        body['status'] = 'success'
    except Exception as e:
        #log task
        print(e)
        body['status'] = 'failed'
    body['type'] = 'vm'
    networkNotificationTask(broker, body)
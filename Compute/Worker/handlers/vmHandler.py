#!/usr/bin/python3.6
database = ''
broker = ''
from lib2 import base
base.database = database
from .tasks import networkTask, vmNotificationTask
import json


def set_config(db, brkr):
    base.database = db
    global database
    global broker
    database = db
    broker = brkr


def post(body_dict):
    from lib2.areaOps import area
    try:
        a = area().get(name=body_dict['area'])
        v = a.create_vm(
            name = body_dict["name"],
            owner = body_dict["owner"],
            ip = body_dict["ip"],
            networks = [net_dict["name"] for net_dict in body_dict["networks"]],
            cpu = body_dict["cpu"],
            memory = body_dict["ram"],
            size = body_dict["disk"],
            password = body_dict["password"],
            template = body_dict["template"]
        )
        if 'status' not in body_dict.keys():
            netReq_dict = {}
            netReq_dict['retries'] = body_dict['retries']
            netReq_dict['id'] = body_dict['id']
            netReq_dict['method'] = 'POST'
            netReq_dict['networks'] = v.network_map
            netReq_dict['vm'] = body_dict['name']
            netReq_dict['owner'] = body_dict['owner']
            netReq_dict['type'] = 'vm'
            networkTask(broker, netReq_dict)
        body_dict['status'] = 'success'
    except Exception as e:
        body_dict['status'] = 'failed'
    vmNotificationTask(broker, body_dict)

    

def put(body_dict):
    pass



def delete(body_dict):
    from lib2.computeOps import vm
    try:
        v = vm().get(body_dict['name'], body_dict['owner'])
        if 'status' not in body_dict.keys():
            netReq_dict = {}
            netReq_dict['id'] = body_dict['id']
            netReq_dict['method'] = 'DELETE'
            netReq_dict['vm'] = body_dict['name']
            netReq_dict['owner'] = body_dict['owner']
            netReq_dict['networks'] = v.network_map
            netReq_dict['type'] = 'vm'
            networkTask(broker, netReq_dict)
        flag_dict = v.delete()
        body_dict['status'] = 'success'
        for val in flag_dict.values():
            if val:
                body_dict['status'] = 'failed'
                break
    except Exception as e:
        body_dict['status'] = 'failed'
    vmNotificationTask(broker, body_dict)
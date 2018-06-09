#!/usr/bin/python3.6
from lib2 import base
base.database = '172.17.0.1'
from .tasks import networkTask, vmNotificationTask
database = ''
broker = ''
import json
from lib2.areaOps import area
from lib2.computeOps import vm

def post(body_dict):
    ns = [net_dict["name"] for net_dict in body_dict["networks"]]
    print(ns)
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
        netReq_dict = {}
        netReq_dict['method'] = 'POST'
        netReq_dict['networks'] = v.network_map
        networkTask(broker, netReq_dict)
        body_dict['status'] = 'success'
    except Exception as e:
        print(e)
        body_dict['status'] = 'failed'
    vmNotificationTask(broker, body_dict)

    

def put(body_dict):
    pass



def delete(body_dict):
    try:
        v = vm().get(body_dict['name'], body_dict['owner'])
        print(v)
        netReq_dict = {}
        netReq_dict['method'] = 'DELETE'
        netReq_dict['networks'] = v.network_map
        networkTask(broker, netReq_dict)
        v.delete()
        body_dict['status'] = 'success'
    except Exception as e:
        print(e)
        body_dict['status'] = 'failed'
    vmNotificationTask(broker, body_dict)
#!/usr/bin/python3.6
from lib2 import base
base.database = '172.17.0.1'
from .tasks import networkTask
database = ''
broker = ''
import json
from lib2.areaOps import area
from lib2.computeOps import vm

def post(body_dict):
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
    netReq_dict['networks'] = v.network_map
    networkTask(broker, json.loads(netReq_dict))

    

def put(body_dict):
    pass

def delete(body_dict):
    v = vm().get(body_dict['name'], body_dict['owner'])
    v.delete()
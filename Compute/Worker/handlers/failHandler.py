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


def recover(body):
    from lib2.areaOps import area
    a = area().get(name=body['area'])
    a.failHost(body['host'])
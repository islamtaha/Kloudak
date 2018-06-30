#!/usr/bin/python3.6
import json, pika
import helpers
from tasks import dispatch

def vmRollback(task, inventory, broker, body={}):
    from helpers import api_call
    '''
    if method == POST:
        1- delete the entry in inventory
        2- if vm_notification:
            delete network entries in network service
          else:
            delete vm from compute service
    if method == DELETE:
        add entry to inventory
        log task
    '''
    owner = task.owner
    name = task.objectName
    body = {
        'owner': owner,
        'name': name,
        'method': task.method,
        'type': 'vm'
    }
    print(body)
    if task.method == 'POST':
        if 'networks' in body.keys():
            #failed at network config. delete vm
            dispatch(json.dumps(body), 'vm_rollback', broker)
        else:
            #delete interfaces at network service
            dispatch(json.dumps(body), 'network_rollback', broker)
        url = f'{inventory}{owner}/vms/{name}/'
        api_call('delete', url)
    elif task.method == 'DELETE':
        #add log entry
        pass

        


def networkRollback(task, inventory, borker):
    from helpers import api_call
    """
    1- if method == POST:
        delete the entry in inventory
       if method == DELETE:
        add entry to inventory
    """
    owner = task.owner
    name = task.objectName
    if task.method == 'POST':
        url = f'{inventory}{owner}/networks/{name}/'
        api_call('delete', url)
    elif task.method == 'DELETE':
        #add log entry
        url = f'{inventory}{owner}/networks/'
        body = {
            'name': name,
            'description': ''
        }
        api_call('post', url, body)


def routerRollback(task, inventory, borker):
    """
    1- if method == POST:
        delete the entry in inventory
       if method == DELETE:
        add entry to inventory
    """
    pass


def interfaceRollback(task, inventory, borker):
    """
    1- if method == POST:
        delete the entry in inventory
       if method == DELETE:
        add entry to inventory
    """
    pass
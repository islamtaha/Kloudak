#!/usr/bin/python3.6

import requests
import ipaddress
import json
from .exceptions import GetAreaException
from .base import InventoryObject


class area(InventoryObject):
    '''interface to interact with area objects stored in inventory
    '''
    def __init__(self, *args, **kwargs):
        self.name = ''
        self.subnet = ''
        self.next_ip = ''
        if 'name' in kwargs.keys():
            self.name = kwargs['name']
        if 'subnet' in kwargs.keys():
            self.subnet = kwargs['subnet']
            if 'next_ip' in kwargs.keys():
                self.next_ip = kwargs['next_ip']
            else:
                ip = str(ipaddress.ip_interface(self.subnet).ip + 1)
                prefix = self.subnet.split('/')[1]
                self.next_ip = ip + prefix

    
    def __str__(self):
        return self.name
    
    
    @classmethod
    def get(cls, InventoryIP, InventoryPort, name):
        '''retruns with an object of requested area if available
        - returns None if no area matches the specified name
        - raises GetAreaException
        - example:
            a = area().get('127.0.0.1', '5000', 'Area-01')
        '''
        requested_name = name
        inventoryURL = f"http://{InventoryIP}:{InventoryPort}/areas/{requested_name}/"
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetAreaException(f'connection refused')
        if res.status_code == 200:
            res_dict = json.loads(res.text)
            return cls(
                name=res_dict['name'],
                subnet=res_dict['subnet'],
                next_ip=res_dict['next_ip']
                )
        elif res.status_code == 404:
            return None
        else:
            raise GetAreaException(f'inventory request returned with status code {res.status_code}')


    @classmethod
    def getAll(cls, InventoryIP, InventoryPort):
        '''return with a list of all areas
            - raises GetAreaException
            - example:
                alist = area().getall('127.0.0.1', '5000')
        '''
        inventoryURL = f"http://{InventoryIP}:{InventoryPort}/areas/"
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetAreaException(f'connection refused')
        res_dict = json.loads(res.text)
        if bool(res_dict['areas'][0]):
            areas = [cls().get(InventoryIP, InventoryPort, name=a['name']) for a in res_dict['areas']]
        else:
            areas = []
        return areas

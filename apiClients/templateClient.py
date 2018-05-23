#!/usr/bin/python3.6

import requests
import ipaddress
import json
from .exceptions import GetTemplateException
from .base import InventoryObject


class template(InventoryObject):
    '''interface to interact with area objects stored in inventory
    '''
    def __init__(self, *args, **kwargs):
        self.name = ''
        self.description = ''
        self.os = ''
        self.cpu = 0
        self.ram = 0
        self.disk = 0
        if 'name' in kwargs.keys():
            self.name = kwargs['name']
        if 'description' in kwargs:
            self.description = kwargs['description']
        if 'os' in kwargs:
            self.os = kwargs['os']
        if 'cpu' in kwargs:
            self.cpu = kwargs['cpu']
        if 'ram' in kwargs:
            self.ram = kwargs['ram']
        if 'disk' in kwargs:
            self.disk = kwargs['disk']

    
    def __str__(self):
        return self.name
    
    
    @classmethod
    def get(cls, InventoryIP, InventoryPort, name):
        '''retruns with an object of requested template if available
        - returns None if no template matches the specified name
        - raises GetTemplateException
        - example:
            t = template().get('127.0.0.1', '5000', 'Area-01')
        '''
        requested_name = name
        inventoryURL = f"http://{InventoryIP}:{InventoryPort}/templates/{requested_name}/"
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetTemplateException(f'connection refused')
        if res.status_code == 200:
            res_dict = json.loads(res.text)
            return cls(
                name=res_dict['name'],
                description=res_dict['description'],
                os=res_dict['os'],
                ram=res_dict['ram'],
                cpu=res_dict['cpu'],
                disk=res_dict['disk']
                )
        elif res.status_code == 404:
            return None
        else:
            raise GetTemplateException(f'inventory request returned with status code {res.status_code}')


    @classmethod
    def getAll(cls, InventoryIP, InventoryPort):
        '''return with a list of all templates
            - raises GetTemplateException
            - example:
                tlist = template().getall('127.0.0.1', '5000')
        '''
        inventoryURL = f"http://{InventoryIP}:{InventoryPort}/templates/"
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetTemplateException(f'connection refused')
        res_dict = json.loads(res.text)
        if bool(res_dict['templates'][0]):
            templates = [cls().get(InventoryIP, InventoryPort, name=a['name']) for a in res_dict['templates']]
        else:
            templates = []
        return templates

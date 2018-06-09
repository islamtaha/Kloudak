import requests
from .decorators import retry
from django.apps import apps
from .exceptions import MethodNotSupportedException
import jwt

retries = 1
wait = 0
appConfig = apps.get_app_config('ControllerAPI')
retries = appConfig.retries
wait = appConfig.wait


def set_retries(n):
    global retries
    if isinstance(n, int):
        retries = n

def set_wait(n):
    global wait
    if isinstance(n, int):
        wait = n

@retry(retries=retries, wait=wait)
def network_validation(addr, name, owner):
    '''----validates the existence of a network object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/networks/' + name + '/'
    payload = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'mykey'}
    jwt_token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    headers = {'token': jwt_token.decode('utf-8')}
    res = requests.get(url, headers=headers)
    return res.status_code


@retry(retries=retries, wait=wait)
def vm_validation(addr, name, owner):
    '''----validates the existence of a vm object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/vms/' + name + '/'
    payload = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'mykey'}
    jwt_token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    headers = {'token': jwt_token.decode('utf-8')}
    res = requests.get(url, headers=headers)
    return res.status_code


@retry(retries=retries, wait=wait)
def router_validation(addr, name, owner):
    '''----validates the existence of a router object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/routers/' + name + '/'
    payload = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'mykey'}
    jwt_token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    headers = {'token': jwt_token.decode('utf-8')}
    res = requests.get(url, headers=headers)
    return res.status_code


@retry(retries=retries, wait=wait)
def interface_validation(addr, router, owner, network):
    '''----validates the existence of an interface object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/routers/' + router + '/interfaces/' + network + '/'
    payload = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'mykey'}
    jwt_token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    headers = {'token': jwt_token.decode('utf-8')}
    res = requests.get(url, headers=headers)
    return res.status_code


@retry(retries=retries, wait=wait)
def api_call(method, url, body=''):
    '''----this function is used to execute REST requests----
        - Supported methods are ['post', 'get', 'put', 'delete']
        - returns http response object (of requests)
        - raises MethodNotSupportedException
    '''
    calls = {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put,
        'delete': requests.delete
        }
    payload = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'mykey'}
    jwt_token = jwt.encode(payload, "SECRET_KEY", algorithm="HS256")
    headers = {'token': jwt_token.decode('utf-8')}
    if method not in calls.keys():
        raise MethodNotSupportedException
    if method == 'post' or method == 'put':
        return calls[method](url, data=body, headers=headers)
    return calls[method](url, headers=headers)
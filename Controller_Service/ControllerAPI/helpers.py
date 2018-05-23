import requests
from .decorators import retry
from django.apps import apps
from .exceptions import MethodNotSupportedException


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
    res = requests.get(url)
    return res.status_code


@retry(retries=retries, wait=wait)
def vm_validation(addr, name, owner):
    '''----validates the existence of a vm object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/vms/' + name + '/'
    res = requests.get(url)
    return res.status_code


@retry(retries=retries, wait=wait)
def router_validation(addr, name, owner):
    '''----validates the existence of a router object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/routers/' + name + '/'
    res = requests.get(url)
    return res.status_code


@retry(retries=retries, wait=wait)
def interface_validation(addr, router, owner, network):
    '''----validates the existence of an interface object----
        -returns the status code of calling the object in Inventory API
    '''
    url = addr + owner + '/routers/' + router + '/interfaces/' + network + '/'
    res = requests.get(url)
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
    if method not in calls.keys():
        raise MethodNotSupportedException
    if method == 'post' or method == 'put':
        return calls[method](url, body)
    return calls[method](url)
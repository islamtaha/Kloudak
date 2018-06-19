#!/usr/bin/python3.6
import requests, jwt
from decorators import retry


retries=1
wait=0

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
        raise Exception('invalid method')
    if method == 'post' or method == 'put':
        return calls[method](url, data=body, headers=headers)
    return calls[method](url, headers=headers)
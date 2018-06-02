from django.http import HttpResponse
import json, jwt
from rest_framework import status
from broker_tasks import network
from .helpers import network_validation
from .helpers import api_call
from .exceptions import MissingKeyException
from .models import networkTask


class networkRequest(object):
    '''----class for handling network API requests----
        - initialized with an object of the request, inventory address, broker ip
        - process_request function returns the appropriate HttpResult object
        - raises MissingKeyException
    '''
    def __init__(self, request, inv_addr, broker):
        self.request = request
        self.method = self.request.method
        self.body = {}
        self.inv_addr = inv_addr
        self.broker = broker


    def process_request(self):
        self._common_decode(self.request)
        if self.method == 'POST':
            self._decode_post(self.request)
            response = self._process_post()
        elif self.method == 'DELETE':
            response = self._process_delete()
        elif self.method == 'PUT':
            self._decode_put(self.request)
            response = self._process_put()
        return response
    

    def _common_decode(self, request):
        self.req_str = request.body.decode("utf-8", errors="strict")
        self.req_dict = json.loads(self.req_str)
        try:
            self.owner = self.req_dict['owner']
            self.name = self.req_dict['name']
        except:
            raise MissingKeyException


    def _decode_put(self, request):
        try:
            self.update_dict = self.req_dict['update_dict']
            self.new_name = self.update_dict['name']
            self.new_description = self.update_dict['description']
        except:
            raise MissingKeyException


    def _process_put(self):
        code = network_validation(self.inv_addr, self.name, self.owner)
        if code == 404:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if code == 200:
            #publish task to network queue
            task = network.networkTasks(name=self.name, owner=self.owner, broker=self.broker)
            task.update(
                new_name=self.new_name, 
                new_description=self.new_description,
                )
            body = {
                'name': self.update_dict['name'],
                'description': self.update_dict['description'],
                'state': 'U'
            }
            url = self.inv_addr + self.owner + '/networks/' + self.name + '/'
            api_call(method='put', url=url, body=json.dumps(body))
            return HttpResponse(self.req_str, status=status.HTTP_200_OK)


    def _process_delete(self):
        #validate network
        code = network_validation(self.inv_addr, self.name, self.owner)
        if code == 404:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if code == 200:
            #publish task
            task = network.networkTasks(name=self.name, owner=self.owner, broker=self.broker)
            task.delete()
            url = self.inv_addr + self.owner + '/networks/' + self.name + '/'
            del_req = api_call(method='delete', url=url)
            if del_req.status_code != 202:
                return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(status=status.HTTP_202_ACCEPTED)


    def _decode_post(self, request):
        try:
            self.description = self.req_dict['description']
        except:
            raise MissingKeyException


    def _process_post(self):
        #validate network
        code  = network_validation(self.inv_addr, self.name, self.owner)
        if code != 404:
            return HttpResponse(status=status.HTTP_409_CONFLICT)
        #dispatch task
        task = network.networkTasks(
                    name=self.name,
                    owner=self.owner,
                    description = self.description,
                    broker=self.broker
                    )
        task.create()
        body = {"name": self.name, "description": self.description, "state": "C"}
        try:
            url = self.inv_addr + self.owner + '/networks/'
            api_call(method='post', url=url, body=json.dumps(body))
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return HttpResponse(self.req_str, status=status.HTTP_200_OK)


    def log_task(self):
        #log task
        token = self.request.META['HTTP_TOKEN']
        token_dict = jwt.decode(token.encode('utf-8'), "SECRET_KEY", algorithm='HS256')
        username = token_dict['username']
        t = networkTask(
		    owner=self.owner,
		    method=self.method,
		    objectName=self.name,
		    task=self.req_str,
            username=username
	        )
        t.save()
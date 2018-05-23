from django.http import HttpResponse
import json
from rest_framework import status
from broker_tasks import interface
from .helpers import router_validation,interface_validation
from .helpers import api_call
from .exceptions import MissingKeyException
from .models import interfaceTask


class interfaceRequest(object):
    '''----class for handling interface API requests----
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
            self._decode_post()
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
            self.router = self.req_dict['router']
            self.network = self.req_dict['network']
        except:
            raise MissingKeyException


    def _decode_post(self):
        try:
            self.ip = self.req_dict['ip']
        except:
            raise MissingKeyException


    def _decode_put(self, request):
        try:
            self.update_dict = self.req_dict['update_dict']
            self.new_ip = self.update_dict['ip']
        except:
            raise MissingKeyException


    def _process_put(self):
        #validate router
        rcode = router_validation(self.inv_addr, self.router, self.owner)
        if rcode != 200:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        #interface validation
        code = interface_validation(self.inv_addr, self.router, self.owner, self.network)
        if code == 404:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if code == 200:
            #publish task to network queue
            task = interface.interfaceTasks(network=self.network, 
                owner=self.owner, 
                broker=self.broker,
                router=self.router
            )
            task.update(
                new_ip=self.new_ip
                )
            body = {
                'ip': self.update_dict['ip'],
            }
            url = self.inv_addr + self.owner + '/routers/' + self.router + '/interfaces/' + self.network + '/'
            api_call(method='put', url=url, body=json.dumps(body))
            return HttpResponse(self.req_str, status=status.HTTP_200_OK)


    def _process_delete(self):
        #validate router
        rcode = router_validation(self.inv_addr, self.router, self.owner)
        if rcode != 200:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        #validate router
        code = interface_validation(self.inv_addr, self.router, self.owner, self.network)
        if code == 404:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if code == 200:
            #publish task
            task = interface.interfaceTasks(
                network=self.network,
                router=self.router, 
                owner=self.owner, 
                broker=self.broker
                )
            task.delete()
            url = self.inv_addr + self.owner + '/routers/' + self.router + '/interfaces/' + self.network + '/'
            del_req = api_call(method='delete', url=url)
            if del_req.status_code != 202:
                return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return HttpResponse(status=status.HTTP_202_ACCEPTED)



    def _process_post(self):
        #validate router
        rcode = router_validation(self.inv_addr, self.router, self.owner)
        if rcode != 200:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        #validate interface
        code  = interface_validation(self.inv_addr, self.router, self.owner, self.network)
        if code == 200:
            return HttpResponse(status=status.HTTP_409_CONFLICT)
        #dispatch task
        task = interface.interfaceTasks(
                    router=self.router,
                    owner=self.owner,
                    broker=self.broker,
                    network=self.network
                    )
        task.create(ip=self.ip)
        body = {"network": self.network, "ip": self.ip}
        try:
            url = self.inv_addr + self.owner + '/routers/' + self.router + '/interfaces/'
            api_call(method='post', url=url, body=json.dumps(body))
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return HttpResponse(self.req_str, status=status.HTTP_200_OK)


    def log_task(self):
        #log task
        t = interfaceTask(
		    owner=self.owner,
		    method=self.method,
		    objectNetwork=self.network,
		    task=self.req_str
	        )
        t.save()
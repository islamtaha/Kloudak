from django.http import HttpResponse
import json, jwt
from rest_framework import status
from broker_tasks import vm
from .helpers import vm_validation
from .helpers import api_call
from .exceptions import MissingKeyException
from .models import vmTask

from QueueMonitoring.wsNotifier import sendNotification

token = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'secret'}
notificationIP = 'localhost'


class vmRequest(object):
    '''----class for handling vm API requests----
        - initialized with an object of the request, inventory address, broker ip
        - process_request function returns the appropriate HttpResult object
        - raises MissingKeyException, Exception 
    '''
    def __init__(self, request, inv_addr, broker, retries=0):
        self.request = request
        self.method = self.request.method
        self.body = {}
        self.inv_addr = inv_addr
        self.broker = broker
        self.retries = retries


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
            self.new_networks = self.update_dict['new_networks']
        except:
            raise MissingKeyException


    def _process_put(self):
        code = vm_validation(self.inv_addr, self.name, self.owner)
        if code == 404:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if code == 200:
            #publish task to vm queue
            t = self.log_task()
            task = vm.vmTasks(name=self.name, owner=self.owner, broker=self.broker, task_id=t.id, retries=self.retries)
            task.update(
                new_name=self.new_name, 
                new_description=self.new_description,
                new_networks=self.new_networks
                )
            body = {
                'name': self.update_dict['name'],
                'description': self.update_dict['description'],
                'networks': self.update_dict['new_networks'],
                'state': 'U'
            }
            url = self.inv_addr + self.owner + '/vms/' + self.name + '/'
            api_call(method='put', url=url, body=json.dumps(body))
            sendNotification(notificationIP, 3000, t.owner, token, t.as_dict())
            return HttpResponse(self.req_str, status=status.HTTP_200_OK)


    def _process_delete(self):
        #validate vm
        code = vm_validation(self.inv_addr, self.name, self.owner)
        if code == 404:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        if code == 200:
            #publish task to vm queue
            t = self.log_task()
            task = vm.vmTasks(name=self.name, owner=self.owner, broker=self.broker, task_id=t.id, retries=self.retries)
            task.delete()
            url = self.inv_addr + self.owner + '/vms/' + self.name + '/'
            del_req = api_call(method='delete', url=url)
            if del_req.status_code != 202:
                return HttpResponse(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            sendNotification(notificationIP, 3000, t.owner, token, t.as_dict())
            return HttpResponse(status=status.HTTP_202_ACCEPTED)


    def _decode_post(self, request):
        try:
            self.description = self.req_dict['description']
            self.area = self.req_dict['area']
            self.temp_name = self.req_dict['template']
            self.networks = self.req_dict['networks']
            self.password = self.req_dict['password']
        except:
            raise MissingKeyException


    def _get_ip(self):
        url = self.inv_addr + 'address/' + self.area + '/ip' + '/'
        ip_req = api_call(method='get', url=url)
        if ip_req.status_code != 200:
            raise Exception(f"can't get ip. return code={ip_req.status_code}")    
        ip_dict = json.loads(ip_req.text)
        self.ip = ip_dict['ip']
        return ip_dict['ip']


    def _get_template_details(self):
        url = self.inv_addr + 'templates/' + self.temp_name + '/'
        temp_details = api_call(method='get', url=url)
        temp_dict = json.loads(temp_details.text)
        self.os = temp_dict['os']
        self.cpu = temp_dict['cpu']
        self.ram = temp_dict['ram']
        self.disk = temp_dict['disk']


    def _process_post(self):
        #validate vm
        code  = vm_validation(self.inv_addr, self.name, self.owner)
        if code != 404:
            return HttpResponse(status=status.HTTP_409_CONFLICT)

        self.ip = self._get_ip()
        self._get_template_details()
        #dispatch task
        t = self.log_task()
        task = vm.vmTasks(name=self.name, owner=self.owner, broker=self.broker, task_id=t.id, retries=self.retries)
        task.netConfig(
                ipaddr=self.ip, 
                networks=self.networks,
                area=self.area
                )
        task.hwConfig(cpu=self.cpu, ram=self.ram, disk=self.disk)
        task.swConfig(
                password=self.password,
                template=self.temp_name,
                os_flavor=self.os
                )
        task.create(description=self.description)
        #post object to inventory
        body={}
        body['name'] = self.name
        body['description'] = self.description
        body['ip'] = self.ip
        body['area'] = self.area
        body['template'] = self.temp_name
        body['networks'] = self.networks
        body['state'] = "U"
        url = self.inv_addr + self.owner + '/vms/'
        api_call(method='post', url=url, body=json.dumps(body))
        res_dict = json.loads(self.req_str)
        res_dict['ip'] = self.ip
        sendNotification(notificationIP, 3000, t.owner, token, t.as_dict())
        return HttpResponse(json.dumps(res_dict), status=status.HTTP_200_OK)


    def log_task(self):
        #log task
        token = self.request.META['HTTP_TOKEN']
        token_dict = jwt.decode(token.encode('utf-8'), "SECRET_KEY", algorithm='HS256')
        username = token_dict['username']
        task_dict = self.req_dict
        task_dict['retries'] = self.retries
        if self.request.method == 'POST':
            task_dict['ip'] = self.ip
        task_str = json.dumps(task_dict)
        t = vmTask(
		    owner=self.owner,
		    method=self.method,
		    objectName=self.name,
		    task=task_str,
            username=username
	        )
        t.save()
        return t
import pika
import json


class vmTasks():
    '''tasks published to vm queue on rabbitMQ broker'''
    def __init__(self, name, owner, broker, task_id=0, retries=0):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='vm')
        self.body = {}
        self.body['id'] = task_id
        self.body['name'] = name
        self.body['owner'] = owner
        self.body['type'] = 'vm'
        self.body['retries'] = retries

    def netConfig(self, ipaddr, networks, area):
        self.body['ip'] = ipaddr
        self.body['networks'] = []
        for n in networks:
            self.body['networks'].append({'name': n})
        self.body['area'] = area

    def hwConfig(self, cpu, ram, disk):
        self.body['cpu'] = cpu
        self.body['ram'] = ram
        self.body['disk'] = disk

    def swConfig(self, password, template, os_flavor):
        self.body['password'] = password
        self.body['template'] = template
        self.body['os'] = os_flavor

    def create(self, description=""):
        '''generates a task in json format structured as:
            {
                "id": <int>,
                "method": "POST",
                "type": "vm"
                "name": "vm name",
                "owner": "owner name",
                "description": "vm description"
                "ip": "vm public ip",
                "networks": [{"name": "network name"},],
                "area": "area name",
                "cpu": cpu_count,
                "ram": memory_size,
                "disk": disk_size,
                "password": "user password",
                "template": "template name",
                "os": "os name",
                "retries": <int>
            }
        '''
        self.body['method'] = 'POST'
        self.body['description'] = description
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='vm', body=jbody)
        self.connection.close()

    def delete(self):
        '''generates a task in json format structured as:
            {
                "method": "DELETE",
                "type": "vm"
                "name": "vm name",
                "owner": "owner name"
            }
        '''
        self.body['method'] = 'DELETE'
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='vm', body=jbody)
        self.connection.close()

    def update(self, new_name, new_description, new_networks):
        '''generates a task in json format structured as:
            {
                "method": "PUT",
                "type": "vm"
                "name": "vm name",
                "owner": "owner name",
                "update_dict": {
                    "name": "new name",
                    "description": "new description",
                    "networks": [{"name": "network name"}]
                }
            }
        '''
        self.body['method'] = 'UPDATE'
        update_dict = {}
        update_dict['name'] = new_name
        update_dict['description'] = new_description
        update_dict['networks'] = new_networks
        self.body['update_dict'] = update_dict
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='vm', body=jbody)
        self.connection.close()
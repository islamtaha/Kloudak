import pika
import json

class routerTasks():
    '''tasks published to network queue on rabbitMQ broker'''
    def __init__(self, name, owner, broker="localhost", task_id=0, retries=0):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='network')
        self.body = {}
        self.body['id'] = task_id
        self.body['name'] = name
        self.body['owner'] = owner
        self.body['type'] = 'router'
        self.body['retries'] = retries
        
    def create(self):
        '''generates a task in json format structured as:
            {
                "method": "POST",
                "type": "router"
                "name": "router name",
                "owner": "owner name",
            }
        '''
        self.body['method'] = 'POST'
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

    def delete(self):
        '''generates a task in json format structured as:
            {
                "method": "DELETE",
                "type": "router"
                "name": "router name",
                "owner": "owner name"
            }
        '''
        self.body['method'] = 'DELETE'
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

    def update(self, new_name):
        '''generates a task in json format structured as:
            {
                "method": "PUT",
                "type": "router"
                "name": "router name",
                "owner": "owner name",
                "update_dict": {
                    "name": "new name",
                    "description": "new description"
                    }
            }
        '''
        self.body['method'] = 'PUT'
        update_dict = {}
        update_dict['name'] = new_name
        self.body['update_dict'] = update_dict
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

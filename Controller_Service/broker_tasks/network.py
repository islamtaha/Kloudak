import pika
import json

class networkTasks():
    '''tasks published to network queue on rabbitMQ broker'''
    def __init__(self, name, owner, broker="localhost", description=""):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='network')
        self.description = description
        self.body = {}
        self.body['name'] = name
        self.body['owner'] = owner
        self.body['type'] = 'network'
        
    def create(self):
        '''generates a task in json format structured as:
            {
                "method": "POST",
                "type": "network"
                "name": "network name",
                "owner": "owner name",
                "description": "network description"
            }
        '''
        self.body['method'] = 'POST'
        self.body['description'] = self.description
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

    def delete(self):
        '''generates a task in json format structured as:
            {
                "method": "DELETE",
                "type": "network"
                "name": "network name",
                "owner": "owner name"
            }
        '''
        self.body['method'] = 'DELETE'
        self.body['description'] = self.description
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

    def update(self, new_name, new_description):
        '''generates a task in json format structured as:
            {
                "method": "PUT",
                "type": "network"
                "name": "network name",
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
        update_dict['description'] = new_description
        self.body['update_dict'] = update_dict
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

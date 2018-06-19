import pika
import json

class interfaceTasks():
    '''tasks published to network queue on rabbitMQ broker'''
    def __init__(self, owner, router, network, broker="localhost", task_id=0, retries=0):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='network')
        self.body = {}
        self.body['id'] = task_id
        self.body['router'] = router
        self.body['network'] = network
        self.body['type'] = 'interface'
        self.body['owner'] = owner
        self.body['retries'] = retries
        
    def create(self, ip):
        '''generates a task in json format structured as:
            {
                "method": "POST",
                "type": "interface"
                "router": "router name",
                "network": "owner name",
                "ip": "ip address"
            }
        '''
        self.body['method'] = 'POST'
        self.body['ip'] = ip
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

    def delete(self):
        '''generates a task in json format structured as:
            {
                "method": "DELETE",
                "type": "interface"
                "router": "router name",
                "network": "owner name"
            }
        '''
        self.body['method'] = 'DELETE'
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

    def update(self, new_ip):
        '''generates a task in json format structured as:
            {
                "method": "PUT",
                "type": "interface"
                "router": "router name",
                "network": "owner name",
                "update_dict": {
                    "ip": "new ip address"
                }
            }
        '''
        self.body['method'] = 'PUT'
        update_dict = {}
        update_dict['ip'] = new_ip
        self.body['update_dict'] = update_dict
        jbody = json.dumps(self.body)
        self.channel.basic_publish(exchange='', routing_key='network', body=jbody)
        self.connection.close()

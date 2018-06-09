import pika, json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare('vm')

pbody = {
                "method": "DELETE",
                "type": "vm",
                "name": "VM-27",
                "owner": "Workspace-01",
                "description": "",
                "ip": "10.10.10.50/24",
                "networks": [{"name": "Network-01"},],
                "area": "Area-01",
                "cpu": 1,
                "ram": 2,
                "disk": 10,
                "password": "Maglab123!",
                "template": "Template-01.raw",
                "os": "Fedora"
            }

channel.basic_publish(exchange='', routing_key='vm', body=json.dumps(pbody))
connection.close()

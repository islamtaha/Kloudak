import pika, json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare('vm')

pbody = {
                "method": "POST",
                "type": "network",
                "name": "Network-01",
                "owner": "Workspace-01",
                "description": "",
                "id": "6",
                "status": "success"
            }

channel.basic_publish(exchange='', routing_key='network_notification', body=json.dumps(pbody))
connection.close()

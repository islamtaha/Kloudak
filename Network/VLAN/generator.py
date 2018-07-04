import pika, json

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

rbody = {"owner": "MU-DataCenter", "name": "WS-Net", "method": "POST", "type": "network"}

channel.basic_publish(exchange='', routing_key='network', body=json.dumps(rbody))
connection.close()

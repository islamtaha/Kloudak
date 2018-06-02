import pika
import json

def handler(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    print(data)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

print("handling connection")
channel.basic_consume(handler, queue='vm', no_ack=True)
channel.start_consuming()

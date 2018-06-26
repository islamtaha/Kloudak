#!/usr/bin/python3.6
import pika
import json
from lib.NetworkOps import Interface

def handler(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    name = data['name']
    owner = data['owner']




if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    print("handling connection")
    channel.basic_consume(handler, queue='network_rollback', no_ack=True)
    channel.start_consuming()

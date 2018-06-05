#!/usr/bin/python3.6

import pika
import json


def networkTask(broker, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()
    channel.queue_declare(queue='network')
    jbody = json.dumps(body)
    channel.basic_publish(exchange='', routing_key='network', body=jbody)
    connection.close()
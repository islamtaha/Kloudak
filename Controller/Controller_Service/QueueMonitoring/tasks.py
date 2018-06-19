#!/usr/bin/python3.6

import pika, json

def dispatch(body, queue, broker):
    connection = pika.BlockingConnection(pika.ConnectionParameters(broker))
    channel = connection.channel()
    channel.queue_declare(queue)
    channel.basic_publish(exchange='', routing_key=queue, body=body)
    connection.close()
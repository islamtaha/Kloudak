#!/usr/bin/python3.6

import pika, json

def networkNotificationTask(broker, body):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()
    channel.queue_declare(queue='network_notification')
    jbody = json.dumps(body)
    channel.basic_publish(exchange='', routing_key='network_notification', body=jbody)
    connection.close()
#/usr/bin/python3.6
import pika
import json


def host_failure(host, area, broker):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()
    channel.queue_declare(queue='failure')
    body = {'host': host, 'status': False, 'area': area}
    jbody = json.dumps(body)
    channel.basic_publish(exchange='', routing_key='failure', body=jbody)
    connection.close()
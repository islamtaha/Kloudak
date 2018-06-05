#!/bin/python3.6
import pika
import json
from config import get_config
from lib2 import base
from handlers import vmHandler


conf_file = 'conf.json'
conf_dict = get_config(conf_file)

def method_mapper(method, handler):
    method_dict = {
        'POST': handler.post,
        'PUT': handler.put,
        'DELETE': handler.delete
    }
    return method_dict[method]


def handler_mapper(t):
    handler_dict = {
        'vm': vmHandler,
    }
    return handler_dict[t]


def consumer(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    t = data['type']
    handler = handler_mapper(t)
    handler.database = conf_dict['database']
    handler.broker = conf_dict['broker']
    base.database = conf_dict['database']
    method = method_mapper(data['method'], handler)
    method(data)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=conf_dict['broker']))
    channel = connection.channel()
    channel.queue_declare(queue='vm')
    print("handling connection")
    channel.basic_consume(consumer, queue='vm', no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(1)
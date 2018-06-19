#!/usr/bin/python3.6

from config import get_config
from handlers import networkHandler, vmHandler, routerHandler
import pika, json


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
        'network': networkHandler,
        'vm': vmHandler,
        'router': routerHandler
    }
    return handler_dict[t]


def consumer(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    t = data['type']
    handler = handler_mapper(t)
    handler.set_config(conf_dict['database'], conf_dict['broker'])
    method = method_mapper(data['method'], handler)
    method(data)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=conf_dict['broker']))
    channel = connection.channel()
    channel.queue_declare(queue='vm')
    print("handling connection")
    channel.basic_consume(consumer, queue='network', no_ack=False)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(1)
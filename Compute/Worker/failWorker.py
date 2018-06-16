#!/bin/python3.6
import pika
import json
from config import get_config
from handlers import failHandler 

conf_file = 'conf.json'
conf_dict = get_config(conf_file)

def consumer(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    failHandler.set_config(conf_dict['database'], conf_dict['broker'])
    failHandler.recover(data)


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=conf_dict['broker']))
    channel = connection.channel()
    channel.queue_declare(queue='failure')
    print("handling connection")
    channel.basic_consume(consumer, queue='failure', no_ack=True)
    channel.start_consuming()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit(1)
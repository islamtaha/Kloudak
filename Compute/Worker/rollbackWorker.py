#!/usr/bin/python3.6
import pika
import json
from lib2 import base
base.database = '172.17.0.1'
from lib2.computeOps import vm

def handler(ch, ch_method, properties, body):
    data = json.loads(body.decode('utf-8'))
    name = data['name']
    owner = data['owner']
    v = vm().get(name=name, owner=owner)
    flag_dict = v.delete()
    flags = []
    for flag in flag_dict.keys():
        if flag_dict[flag]:
            flags.append(flag)
        if len(flags) > 0:
            line = f"method={data['method']},owner={owner},vm={name},flags={f for f in flags}"
            #log line
    ch.basic_ack(delivery_tag=ch_method.delivery_tag)



if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    print("handling connection")
    channel.basic_consume(handler, queue='vm_rollback', no_ack=False)
    channel.start_consuming()

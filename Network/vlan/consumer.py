import pika
import json
import ovsNetwork
import NetworkDB

from config import broker, key


def handler(ch, method, properties, body):
    ch.basic_ack(delivery_tag = method.delivery_tag)

    data = json.loads(body.decode('utf-8'))
    if 'host' in data.keys():
        body = {}
        #consume messages from compute service
        name = data['name']
        owner = data['owner']
        host = data['host']
        iface = data['iface']
        network = NetworkDB.privateNetwork(name=name, owner=owner)
        vlan_id = network.getID()
        if vlan_id:
            conf = ovsNetwork.VLANConf(iface=iface, host=host, vlan_id=vlan_id, key_path=key)
            res = conf.add()
        else:
            #log the message to syslog
            msg = f'failed to get vlan_id with error {network.error}'
            body['status'] = 'failed'

        conn = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
        chan = conn.channel()
        body['name'] = name
        body['owner'] = owner
        body['iface'] = iface
        if not res:
            #log msg to syslog
            msg = f'failed to add iface {iface} to vlan {vlan_id} with error {conf.error}'
            body['status'] = 'failed'
        else:
            body['status'] = 'success'
        jbody = json.dumps(body)
        chan.basic_publish(
                exchange='',
                routing_key='network_notification',
                body=jbody
                )
        conn.close()
    else:
        #consume messages from controller
        print(f'recieved {data} from controller')
        method = data['method']
        name = data['name']
        owner = data['owner']
        network = NetworkDB.privateNetwork(name=name, owner=owner)
        if method == 'POST':
            res = network.create()
            if res == 0:
                return 0
            else:
                #log message to syslog
                msg = f'failed to create network with error {network.error}'
                return 1
        elif method == 'DELETE':
            res = network.delete()
            if res == 0:
                return 0
            else:
                #log message to syslog
                msg = f'failed to delete network with error {network.error}'
                return 1


if __name__ == '__main__':
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()
    channel.basic_consume(handler, queue='network')
    channel.start_consuming()

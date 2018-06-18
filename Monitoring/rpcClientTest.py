import pika
import uuid
import json

class PoolRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body.decode('utf-8'))

    def call(self, size, area):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.queue_declare(queue='pool_rpc_queue')
        self.channel.basic_publish(exchange='',
                                   routing_key='pool_rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to = self.callback_queue,
                                         correlation_id = self.corr_id,
                                         ),
                                   body=json.dumps({'size': size, 'area': area}))
        while self.response is None:
            self.connection.process_data_events()
        return self.response['name']


pool_rpc = PoolRpcClient()

print(" [x] Requesting Pool(10, 'Area-01')")
response = pool_rpc.call(10, 'Area-01')
print(" [.] Got %r" % response)
import os, sys, pika, json

#proj_path = "/home/maged/gradproject/Controller_Service/"
proj_path = ".."
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Controller_Service.settings")
sys.path.append(proj_path)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from ControllerAPI.models import interfaceTask, networkTask, routerTask



def handler(ch, method, properties, body):
    data = json.loads(body.decode('utf-8'))
    print(data)


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

print("handling connection")
channel.basic_consume(handler, queue='network_notification', no_ack=True)
channel.start_consuming()
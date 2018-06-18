#!/usr/bin/python3.6
import os, sys, pika, json
from websocket import create_connection
import jwt
import daemon
from wsNotifier import sendNotification


proj_path = ".."
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Controller_Service.settings")
sys.path.append(proj_path)
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from django.apps import apps
from ControllerAPI.models import vmTask

appConfig = apps.get_app_config('ControllerAPI')
notificationIP = appConfig.notif_addr
broker = appConfig.broker


def rollBack(task):
    pass



def fetchTask(task_id, task_type, failed=False):
    if task_type == 'vm':
        vTask = vmTask.objects.get(id=task_id)
        vTask.failed = failed
        vTask.vmConf = True
        if vTask.netConf:
            vTask.finished = True
        vTask.save()
        return vTask


def handler(ch, method, properties, nbody):
    body = json.loads(nbody.decode('utf-8'))
    task_type = body['type']
    task_id = body['id']
    if body['status'] == 'failed':
        task_failed = True
    else:
        task_failed = False
    
    t = fetchTask(task_id, task_type, task_failed)
    token = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'secret'}
    sendNotification(notificationIP, 3000, body['owner'], token, t.as_dict())


if __name__ == '__main__':
    with daemon.DaemonContext():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
        channel = connection.channel()
        channel.basic_consume(handler, queue='vm_notification', no_ack=True)
        channel.start_consuming()
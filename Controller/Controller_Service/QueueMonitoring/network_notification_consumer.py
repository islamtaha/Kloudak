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
from ControllerAPI.models import interfaceTask, networkTask, routerTask, vmTask

appConfig = apps.get_app_config('ControllerAPI')
notificationIP = appConfig.notif_addr
broker = appConfig.broker


def rollBack(task):
    pass



def fetchTask(task_id, task_type, failed=False):
    if task_type == 'vm':
        vTask = vmTask.objects.get(id=task_id)
        vTask.failed = failed
        vTask.netConf = True
        if vTask.vmConf:
            vTask.finished = True
        vTask.save()
        return vTask
    if task_type == 'router':
        rTask = routerTask.objects.get(id=task_id)
        rTask.finished = True
        rTask.failed = failed
        rTask.save()
        return rTask
    if task_type == 'network':
        nTask = networkTask.objects.get(id=task_id)
        nTask.finished = True
        nTask.failed = failed
        nTask.save()
        return nTask
    if task_type == 'interface':
        iTask = interfaceTask.objects.get(id=task_id)
        iTask.finished = True
        iTask.failed = failed
        iTask.save()
        return iTask


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
        channel.basic_consume(handler, queue='network_notification', no_ack=True)
        channel.start_consuming()
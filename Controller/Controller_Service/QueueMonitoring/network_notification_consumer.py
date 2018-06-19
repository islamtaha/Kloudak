#!/usr/bin/python3.6
import os, sys, pika, json
from websocket import create_connection
import jwt
import daemon
from wsNotifier import sendNotification
from tasks import dispatch


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
inventory = appConfig.inv_addr
retries = appConfig.retries
wait = appConfig.wait
import rollback
rollback.wait = wait
rollback.retries = retries
from rollback import networkRollback, vmRollback, routerRollback, interfaceRollback




def retry(task, body={}):
    if isinstance(task, vmTask):
        body['retries'] = body['retries'] - 1
        dispatch(json.dumps(body), 'network', broker)
    else:
        body_dict = json.loads(task.task)
        body_dict['retries'] = body_dict['retries'] - 1
        body_dict['status'] = 'failed'
        if isinstance(task, networkTask):
            body_dict['type'] = 'network'
        elif isinstance(task, routerTask):
            body_dict['type'] = 'router'
        elif isinstance(task, interfaceTask):
            body_dict['type'] = 'interface'
        body_dict['id'] = task.id
        body_dict['method'] = task.method   
        body = json.dumps(body_dict)
        dispatch(body, 'network', broker)
        task.task = body
        task.save()


def fetchTask(task_id, task_type, retries, failed=False, body=''):
    if task_type == 'vm':
        vTask = vmTask.objects.get(id=task_id)
        if failed:
            if retries > 0:
                retry(vTask, body)
                return None
            else:
                vmRollback(vTask, inventory, broker, body)
        vTask.failed = failed
        vTask.netConf = True
        if vTask.vmConf:
            vTask.finished = True
        vTask.save()
        return vTask
    if task_type == 'router':
        rTask = routerTask.objects.get(id=task_id)
        if failed:
            if retries > 0:
                retry(rTask)
                return None
            else:
                routerRollback(rTask, inventory, broker)
        rTask.finished = True
        rTask.failed = failed
        rTask.save()
        return rTask
    if task_type == 'network':
        nTask = networkTask.objects.get(id=task_id)
        if failed:
            if retries > 0:
                retry(nTask)
                return None
            else:
                networkRollback(nTask, inventory, broker)
        nTask.finished = True
        nTask.failed = failed
        nTask.save()
        return nTask
    if task_type == 'interface':
        iTask = interfaceTask.objects.get(id=task_id)
        if failed:
            if retries > 0:
                retry(iTask)
                return None
            else:
                interfaceRollback(iTask, inventory, broker)
        iTask.finished = True
        iTask.failed = failed
        iTask.save()
        return iTask


def handler(ch, method, properties, nbody):
    body = json.loads(nbody.decode('utf-8'))
    task_type = body['type']
    task_id = body['id']
    retries = body['retries']
    if body['status'] == 'failed':
        task_failed = True
    else:
        task_failed = False
    
    t = fetchTask(task_id, task_type, retries, task_failed, body)
    token = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'secret'}
    sendNotification(notificationIP, 3000, body['owner'], token, t.as_dict())


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()
    channel.queue_declare('network_notification')
    channel.basic_consume(handler, queue='network_notification', no_ack=False)
    channel.start_consuming()

if __name__ == '__main__':
    #with daemon.DaemonContext():
    #    main()
    main()
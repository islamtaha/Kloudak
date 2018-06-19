#!/usr/bin/python3.6
import os, sys, pika, json
from websocket import create_connection
import jwt
import daemon
from wsNotifier import sendNotification
from tasks import dispatch
from rollback import vmRollback


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
inventory = appConfig.inv_addr
retries = appConfig.retries
wait = appConfig.wait
import rollback
rollback.wait = wait
rollback.retries = retries
from rollback import networkRollback, vmRollback, routerRollback, interfaceRollback



def retry(task):
    body_dict = json.loads(task.task)
    body_dict['id'] = task.id
    body_dict['method'] = task.method
    if isinstance(task, vmTask):
        body_dict['retries'] = body_dict['retries'] - 1
        body_dict['status'] = 'failed'
        body_dict['type'] = 'vm'
        body = json.dumps(body_dict)
        dispatch(body, 'vm', broker)
        task.task = body
        task.save()



def fetchTask(task_id, task_type, retries, failed=False, body={}):
    if task_type == 'vm':
        vTask = vmTask.objects.get(id=task_id)
        if failed:
            if retries > 0:
                retry(vTask)
                return None
            else:
                vmRollback(vTask, inventory, broker, body)
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
    retries = body['retries']
    if body['status'] == 'failed':
        task_failed = True
    else:
        task_failed = False
    
    t = fetchTask(task_id, task_type, retries, task_failed, body)
    if t:
        token = {'username': 'maged', 'email': 'magedmotawea@gmail.com', 'key': 'secret'}
        sendNotification(notificationIP, 3000, body['owner'], token, t.as_dict())



def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    channel = connection.channel()
    channel.queue_declare('vm_notification')
    channel.basic_consume(handler, queue='vm_notification', no_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    #with daemon.DaemonContext():
    #    main()
    main()
        
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from .decorators import supported_methods, body_check, check_permissions
from .vmAPI import vmRequest
from .networkAPI import networkRequest
from .routerAPI import routerRequest
from .interfaceAPI import interfaceRequest
from .exceptions import MissingKeyException
from django.apps import apps
from .models import vmTask, networkTask, routerTask, interfaceTask
import json


appConfig = apps.get_app_config('ControllerAPI')
inv_addr = appConfig.inv_addr
broker = appConfig.broker
retries = appConfig.retries

@csrf_exempt
@supported_methods(['POST', 'PUT', 'DELETE'])
@body_check(['name', 'owner'])
@check_permissions('vm')
def vms(request):
    req = vmRequest(request, inv_addr, broker, retries)
    try:
        res = req.process_request()
    except MissingKeyException as e:
        return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
    #req.log_task()
    return res


@csrf_exempt
@supported_methods(['POST', 'PUT', 'DELETE'])
@body_check(['name', 'owner'])
@check_permissions('network')
def networks(request):
    req = networkRequest(request, inv_addr, broker, retries)
    try:
        res = req.process_request()
    except MissingKeyException as e:
        return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
    #req.log_task()
    return res


@csrf_exempt
@supported_methods(['POST', 'PUT', 'DELETE'])
@body_check(['name', 'owner'])
@check_permissions('router')
def routers(request):
    req = routerRequest(request, inv_addr, broker, retries)
    try:
        res = req.process_request()
    except MissingKeyException as e:
        return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
    #req.log_task()
    return res


@csrf_exempt
@supported_methods(['POST', 'PUT', 'DELETE'])
@body_check(['network', 'owner', 'router'])
@check_permissions('router')
def interfaces(request):
    req = interfaceRequest(request, inv_addr, broker, retries)
    try:
        res = req.process_request()
    except MissingKeyException as e:
        return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
    #req.log_task()
    return res


@csrf_exempt
@supported_methods(['GET'])
def tasks(request):
    owner = request.path.split('/')[2]
    vtasks = vmTask.objects.all().filter(owner=owner)
    ntasks = networkTask.objects.all().filter(owner=owner)
    rtasks = routerTask.objects.all().filter(owner=owner)
    itasks = interfaceTask.objects.all().filter(owner=owner)
    
    res_dict = {}
    if len(vtasks) == 0:
        res_dict['vm_tasks'] = []
    else:
        res_dict['vm_tasks'] = [vtask.as_dict() for vtask in vtasks]
    
    if len(ntasks) == 0:
        res_dict['network_tasks'] = []
    else:
        res_dict['network_tasks'] = [ntask.as_dict() for ntask in ntasks]
    
    if len(rtasks) == 0:
        res_dict['router_tasks'] = []
    else:
        res_dict['router_tasks'] = [rtask.as_dict() for rtask in rtasks]
    
    if len(itasks) == 0:
        res_dict['interface_tasks'] = []
    else:
        res_dict['interface_tasks'] = [itask.as_dict() for itask in itasks]

    res_str = json.dumps(res_dict)
    return HttpResponse(res_str, status=status.HTTP_200_OK)


@csrf_exempt
@supported_methods(['GET'])
def running_tasks(request):
    owner = request.path.split('/')[2]
    vtasks = vmTask.objects.all().filter(owner=owner, finished=False)
    ntasks = networkTask.objects.all().filter(owner=owner, finished=False)
    rtasks = routerTask.objects.all().filter(owner=owner, finished=False)
    itasks = interfaceTask.objects.all().filter(owner=owner, finished=False)
    
    res_dict = {}
    if len(vtasks) == 0:
        res_dict['vm_tasks'] = []
    else:
        res_dict['vm_tasks'] = [vtask.as_dict() for vtask in vtasks]
    
    if len(ntasks) == 0:
        res_dict['network_tasks'] = []
    else:
        res_dict['network_tasks'] = [ntask.as_dict() for ntask in ntasks]
    
    if len(rtasks) == 0:
        res_dict['router_tasks'] = []
    else:
        res_dict['router_tasks'] = [rtask.as_dict() for rtask in rtasks]
    
    if len(itasks) == 0:
        res_dict['interface_tasks'] = []
    else:
        res_dict['interface_tasks'] = [itask.as_dict() for itask in itasks]

    res_str = json.dumps(res_dict)
    return HttpResponse(res_str, status=status.HTTP_200_OK)


@csrf_exempt
@supported_methods(['GET'])
def finished_tasks(request):
    owner = request.path.split('/')[2]
    vtasks = vmTask.objects.all().filter(owner=owner, finished=True)
    ntasks = networkTask.objects.all().filter(owner=owner, finished=True)
    rtasks = routerTask.objects.all().filter(owner=owner, finished=True)
    itasks = interfaceTask.objects.all().filter(owner=owner, finished=True)
    
    res_dict = {}
    if len(vtasks) == 0:
        res_dict['vm_tasks'] = []
    else:
        res_dict['vm_tasks'] = [vtask.as_dict() for vtask in vtasks]
    
    if len(ntasks) == 0:
        res_dict['network_tasks'] = []
    else:
        res_dict['network_tasks'] = [ntask.as_dict() for ntask in ntasks]
    
    if len(rtasks) == 0:
        res_dict['router_tasks'] = []
    else:
        res_dict['router_tasks'] = [rtask.as_dict() for rtask in rtasks]
    
    if len(itasks) == 0:
        res_dict['interface_tasks'] = []
    else:
        res_dict['interface_tasks'] = [itask.as_dict() for itask in itasks]

    res_str = json.dumps(res_dict)
    return HttpResponse(res_str, status=status.HTTP_200_OK)

from django.shortcuts import render
#from django.core import serializers
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Network, VM, Area, VMTemplate, FreeIP, Workspace, Router,RouterInterface
from rest_framework import status
import ipaddress
# Create your views here.



@csrf_exempt
def vms(request):
    supported_methods = ["GET", "POST"]

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    req_str = request.body.decode(encoding="utf-8", errors="strict")
    workspace = request.path.split('/')[1]

    if request.method == "GET":
        try:
            user_vms = VM.objects.all().filter(owner=workspace)
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if len(user_vms) == 0:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        dictionaries = json.dumps({'vms' : [{'name': obj.__str__()} for obj in user_vms]})
        return HttpResponse(dictionaries, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            req_dict = json.loads(req_str)
            vm_name = req_dict['name']
            vm_owner = Workspace.objects.get(name=workspace)
            vm_description = req_dict['description']
            vm_ip = req_dict['ip']
            vm_state = req_dict['state']
            vm_area = Area.objects.get(name=req_dict['area'])
            vm_template = VMTemplate.objects.get(name=req_dict['template'])
            #vm_networks = []
            #for network_name in req_dict['networks']:
            #    vm_networks.append(Network.objects.get(name=network_name, owner=vm_owner))
            new_vm = VM(
                name=vm_name, 
                owner=vm_owner, 
                ip=vm_ip,
                description=vm_description,
                state=vm_state,
                area=vm_area,
                template=vm_template
                )
            new_vm.save()
            vm_networks = [Network.objects.get(name=network_name, owner=vm_owner) for network_name in req_dict['networks']]
            if len(vm_networks > 0):
                new_vm.networks.set([Network.objects.get(owner=vm_owner, name=n) for n in vm_networks])
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        res = json.dumps(req_dict)
        return HttpResponse(res, status=status.HTTP_201_CREATED)



@csrf_exempt
def vm_details(request):
    supported_methods = ["GET", "PUT", "DELETE"]
    workspace = request.path.split('/')[1]
    vm_name = request.path.split('/')[3]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == "GET":
        try:
            vm_obj = VM.objects.get(owner=owner, name=vm_name)
        except VM.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = vm_obj.as_dict()
        return HttpResponse(json.dumps(res), status=status.HTTP_200_OK)

    if request.method == "DELETE":
        try:
            vm_obj = VM.objects.get(owner=owner, name=vm_name)
        except VM.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        free_ip = vm_obj.ip
        free_area = vm_obj.area
        vm_obj.delete()
        new_ip = FreeIP(ip=free_ip, area=free_area)
        new_ip.save()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        vm_owner = owner
        req_str = request.body.decode("utf-8", errors="strict")
        try:
            req_dict = json.loads(req_str)
            print('here')
            vm_obj = VM.objects.get(owner=vm_owner, name=vm_name)
            vm_obj.name = req_dict['name']
            vm_obj.description = req_dict['description']
            if bool(req_dict['networks'][0]):
                vm_obj.networks.set([Network.objects.get(name=network_name['name'], owner=vm_owner) for network_name in req_dict['networks']])
            else:
                vm_obj.networks.set([])
            vm_obj.state = req_dict['state']
            vm_obj.save()
        except Exception as e:
            print(e)
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if vm_name != req_dict['name']:
            VM.objects.get(owner=vm_owner, name=vm_name).delete()
        return HttpResponse(req_str, status=status.HTTP_200_OK)



@csrf_exempt
def networks(request):
    supported_methods = ["GET", "POST"]

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    req_str = request.body.decode(encoding="utf-8", errors="strict")
    workspace = request.path.split('/')[1]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        try:
            user_networks = Network.objects.all().filter(owner=owner)
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if len(user_networks) == 0:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        dictionaries = json.dumps({'networks': [{'name': obj.__str__()} for obj in user_networks]})
        return HttpResponse(dictionaries)

    if request.method == "POST":
        try:
            req_dict = json.loads(req_str)
            network_name = req_dict['name']
            network_owner = owner
            network_description = req_dict['description']
            network_state = req_dict['state']
            new_network = Network(name=network_name,
            owner=network_owner,
            description=network_description,
            state=network_state
            )
            new_network.save()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        res = json.dumps(req_dict)
        return HttpResponse(res, status=status.HTTP_201_CREATED)



@csrf_exempt
def network_details(request):
    supported_methods = ["GET", "PUT", "DELETE"]
    workspace = request.path.split('/')[1]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    network_name = request.path.split('/')[3]

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == "GET":
        try:
            network_obj = Network.objects.get(owner=owner, name=network_name)
        except Network.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = network_obj.as_dict()
        return HttpResponse(json.dumps(res), status=status.HTTP_200_OK)

    if request.method == "DELETE":
        try:
            network_obj = Network.objects.get(owner=owner, name=network_name)
        except Network.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        network_obj.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        network_owner = owner
        req_str = request.body.decode("utf-8", errors="strict")
        try:
            req_dict = json.loads(req_str)
            network_obj = Network.objects.get(owner=network_owner, name=network_name)
            network_obj.name = req_dict['name']
            network_obj.description = req_dict['description']
            network_obj.state = req_dict['state']
            network_obj.save()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if network_name != req_dict['name']:
            Network.objects.get(owner=network_owner, name=network_name).delete()
        return HttpResponse(req_str, status=status.HTTP_200_OK)



@csrf_exempt
def areas(request):
    supported_methods = ["GET", "POST"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    req_str = request.body.decode(encoding="utf-8", errors="strict")
    if request.method == "GET":
        try:
            areas = Area.objects.all()
            if len(areas) == 0:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            dictionaries = json.dumps({'areas' : [{'name': obj.__str__()} for obj in areas]})
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(dictionaries, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            req_dict = json.loads(req_str)
            area_name = req_dict["name"]
            area_subnet = req_dict["subnet"]
            area_next_ip = req_dict["next_ip"]
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        new_area = Area(name=area_name, subnet=area_subnet, \
                next_ip=area_next_ip)
        new_area.save()
        return HttpResponse(req_str, status=status.HTTP_201_CREATED)




@csrf_exempt
def area_details(request):
    supported_methods = ["GET", "DELETE", "PUT"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    area_name = request.path.split("/")[2]


    if request.method == "GET":
        try:
            area = Area.objects.get(name=area_name)
        except Area.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = area.as_dict()
        j_res = json.dumps(res)
        return HttpResponse(j_res, status=status.HTTP_200_OK)


    if request.method == "DELETE":
        try:
            area = Area.objects.get(name=area_name)
        except Area.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        area.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        try:
            area = Area.objects.get(name=area_name)
        except Area.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        try:
            req_str = request.body.decode("utf-8", errors="strict")
            req_dict = json.loads(req_str)
            area.name = req_dict['name']
            area.subnet = req_dict['subnet']
            area.next_ip = req_dict['next_ip']
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        area.save()
        if req_dict['name'] != area_name:
            Areas.objects.get(name=area_name).delete()
        return HttpResponse(req_str, status=status.HTTP_202_ACCEPTED)



@csrf_exempt
def area_get_ip(request):
    supported_methods = ["GET"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    area_name = request.path.split("/")[2]
    if request.method == "GET":
        try:
            area = Area.objects.get(name=area_name)
        except Area.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        free_ip_queryset = FreeIP.objects.all().filter(area=Area.objects.get(name=area))
        if len(free_ip_queryset) != 0:
            vm_ip = free_ip_queryset[0]
            res = json.dumps({"ip": str(vm_ip)})
            vm_ip.delete()
            return HttpResponse(res, status=status.HTTP_200_OK)
        subnet = ipaddress.ip_network(area.subnet)
        next_ip = ipaddress.ip_interface(area.next_ip)
        if subnet != next_ip.network:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        vm_ip = next_ip
        next_prefix = str(next_ip.with_prefixlen).split("/")[1]
        ip_str = str((next_ip + 1).ip)
        new_next_ip = ipaddress.ip_interface(ip_str + "/" + next_prefix)
        area.next_ip = str(new_next_ip)
        area.save()
        res = json.dumps({"ip": str(vm_ip)})
        return HttpResponse(res, status=status.HTTP_200_OK)


@csrf_exempt
def templates(request):
    supported_methods = ["GET", "POST"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == "GET":
        try:
            temps = VMTemplate.objects.all()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if len(temps) == 0:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = json.dumps({'templates' : [{'name': obj.__str__()} for obj in temps]})
        return HttpResponse(res, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            req_str = request.body.decode("utf-8", errors="strict")
            req_dict = json.loads(req_str)
            temp_name = req_dict['name']
            temp_os = req_dict['os']
            temp_description = req_dict['description']
            temp_cpu = req_dict['cpu']
            temp_ram = req_dict['ram']
            temp_disk = req_dict['disk']
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        new_temp = VMTemplate(name=temp_name, os=temp_os, \
                description=temp_description, cpu=temp_cpu, \
                ram=temp_ram, disk=temp_disk)
        new_temp.save()
        return HttpResponse(req_str, status=status.HTTP_201_CREATED)



@csrf_exempt
def template_details(request):
    supported_methods = ["GET", "DELETE", "PUT"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    temp_name = request.path.split("/")[2]


    if request.method == "GET":
        try:
            temp = VMTemplate.objects.get(name=temp_name)
        except VMTemplate.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = temp.as_dict()
        j_res = json.dumps(res)
        return HttpResponse(j_res, status=status.HTTP_200_OK)


    if request.method == "DELETE":
        try:
            temp = VMTemplate.objects.get(name=temp_name)
        except VMTemplate.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        temp.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        try:
            temp = VMTemplate.objects.get(name=temp_name)
        except VMTemplate.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        try:
            req_str = request.body.decode("utf-8", errors="strict")
            req_dict = json.loads(req_str)
            temp.name = req_dict['name']
            temp.os = req_dict['os']
            temp.description = req_dict['description']
            temp.cpu = req_dict['cpu']
            temp.ram = req_dict['ram']
            temp.disk = req_dict['disk']
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        temp.save()
        if req_dict['name'] != temp_name:
            VMTemplate.objects.get(name=temp_name).delete()
        return HttpResponse(req_str, status=status.HTTP_200_OK)


@csrf_exempt
def workspace(request):
    supported_methods = ["GET", "POST"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    req_str = request.body.decode(encoding="utf-8", errors="strict")
    if request.method == "GET":
        try:
            workspaces = Workspace.objects.all()
            if len(workspaces) == 0:
                return HttpResponse(status=status.HTTP_404_NOT_FOUND)
            dictionaries = json.dumps({'workspaces' : [{'name': obj.__str__()} for obj in workspaces]})
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(dictionaries, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            req_dict = json.loads(req_str)
            workspace_name = req_dict["name"]
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        new_workspace = Workspace(name=workspace_name)
        new_workspace.save()
        return HttpResponse(req_str, status=status.HTTP_201_CREATED)


@csrf_exempt
def workspace_details(request):
    supported_methods = ["GET", "DELETE", "PUT"]
    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    workspace_name = request.path.split("/")[2]


    if request.method == "GET":
        try:
            workspace = Workspace.objects.get(name=workspace_name)
        except Workspace.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = workspace.as_dict()
        j_res = json.dumps(res)
        return HttpResponse(j_res, status=status.HTTP_200_OK)


    if request.method == "DELETE":
        try:
            workspace = Workspace.objects.get(name=workspace_name)
        except Workspace.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        workspace.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        try:
            workspace = Workspace.objects.get(name=workspace_name)
        except Workspace.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        try:
            req_str = request.body.decode("utf-8", errors="strict")
            req_dict = json.loads(req_str)
            workspace.name = req_dict['name']
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        workspace.save()
        if req_dict['name'] != workspace_name:
            Workspace.objects.get(name=workspace_name).delete()
        return HttpResponse(req_str, status=status.HTTP_200_OK)


@csrf_exempt
def routers(request):
    supported_methods = ["GET", "POST"]

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    req_str = request.body.decode(encoding="utf-8", errors="strict")
    workspace = request.path.split('/')[1]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        try:
            user_routers = Router.objects.all().filter(owner=owner)
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if len(user_routers) == 0:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        dictionaries = json.dumps({'routers': [{'name': obj.__str__()} for obj in user_routers]})
        return HttpResponse(dictionaries, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            req_dict = json.loads(req_str)
            router_name = req_dict['name']
            router_owner = owner
            new_router = Router(name=router_name,
            owner=router_owner
            )
            new_router.save()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        res = json.dumps(req_dict)
        return HttpResponse(res, status=status.HTTP_201_CREATED)


@csrf_exempt
def router_details(request):
    supported_methods = ["GET", "PUT", "DELETE"]
    workspace = request.path.split('/')[1]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    router_name = request.path.split('/')[3]

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == "GET":
        try:
            router_obj = Router.objects.get(owner=owner, name=router_name)
        except Router.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = router_obj.as_dict()
        return HttpResponse(json.dumps(res), status=status.HTTP_200_OK)

    if request.method == "DELETE":
        try:
            router_obj = Router.objects.get(owner=owner, name=router_name)
        except Router.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        router_obj.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        router_owner = owner
        req_str = request.body.decode("utf-8", errors="strict")
        try:
            req_dict = json.loads(req_str)
            router_obj = Router.objects.get(owner=router_owner, name=router_name)
            router_obj.name = req_dict['name']
            router_obj.save()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if router_name != req_dict['name']:
            Router.objects.get(owner=router_owner, name=router_name).delete()
        return HttpResponse(req_str, status=status.HTTP_200_OK)


@csrf_exempt
def interfaces(request):
    supported_methods = ["GET", "POST"]

    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    req_str = request.body.decode(encoding="utf-8", errors="strict")
    workspace = request.path.split('/')[1]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)
    
    router = request.path.split('/')[3]
    try:
        router_obj = Router.objects.get(name=router, owner=owner)
    except Router.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        try:
            router_interfaces = RouterInterface.objects.all().filter(router=router_obj)
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        if len(router_interfaces) == 0:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        dictionaries = json.dumps({'interfaces': [{'name': obj.__str__()} for obj in router_interfaces]})
        return HttpResponse(dictionaries, status=status.HTTP_200_OK)

    if request.method == "POST":
        try:
            req_dict = json.loads(req_str)
            interface_ip = req_dict['ip']
            interface_network = req_dict['network']
            try:
                network_obj = Network.objects.get(name=interface_network, owner=owner)
            except Exception as e:
                return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
            new_interface = RouterInterface(
                router=router_obj,
                ip=interface_ip,
                network=network_obj
            )
            new_interface.save()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        res = json.dumps(req_dict)
        return HttpResponse(res, status=status.HTTP_201_CREATED)


@csrf_exempt
def interface_details(request):
    supported_methods = ["GET", "PUT", "DELETE"]
    workspace = request.path.split('/')[1]
    try:
        owner = Workspace.objects.get(name=workspace)
    except Workspace.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    router_name = request.path.split('/')[3]
    try:
        router_obj = Router.objects.get(owner=owner, name=router_name)
    except Router.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    interface_network = request.path.split('/')[5]
    try:
        network_obj = Network.objects.get(name=interface_network, owner=owner)
    except Network.DoesNotExist:
        return HttpResponse(status=status.HTTP_404_NOT_FOUND)


    if request.method not in supported_methods:
        return HttpResponse(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    if request.method == "GET":
        try:
            interface_obj = RouterInterface.objects.get(network=network_obj, router=router_obj)
        except RouterInterface.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        res = interface_obj.as_dict()
        print(res)
        return HttpResponse(json.dumps(res), status=status.HTTP_200_OK)

    if request.method == "DELETE":
        try:
            interface_obj = RouterInterface.objects.get(network=network_obj, router=router_obj)
        except RouterInterface.DoesNotExist:
            return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        interface_obj.delete()
        return HttpResponse(status=status.HTTP_202_ACCEPTED)

    if request.method == "PUT":
        interface_owner = owner
        req_str = request.body.decode("utf-8", errors="strict")
        try:
            req_dict = json.loads(req_str)
            interface_obj = RouterInterface.objects.get(network=network_obj, router=router_obj)
            interface_obj.ip = req_dict['ip']
            interface_obj.save()
        except Exception as e:
            return HttpResponse(e, status=status.HTTP_400_BAD_REQUEST)
        return HttpResponse(req_str, status=status.HTTP_200_OK)
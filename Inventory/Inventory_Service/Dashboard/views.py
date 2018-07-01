from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from InventoryAPI.models import Workspace, CustomUser, VMTemplate
# Create your views here.


def index(request):
    if not request.user.is_anonymous:
        return redirect('http://localhost:5000/kloudak/workspaces/')
    r = render(request, 'index.html', {})
    return r



@login_required(login_url='http://localhost:5000/kloudak/index/')
def workspaces(request):
    UPs = CustomUser.objects.all().filter(user=request.user)
    if len(UPs) > 0:
        return redirect(f'http://localhost:5000/kloudak/workspaces/{UPs[0].workspace.name}/')
    else:
        r = render(request, 'empty_workspaces.html', {})
    return r


@login_required(login_url='http://localhost:5000/kloudak/index/')
def getWS(request, workspace):
    UPs = CustomUser.objects.all().filter(user=request.user)
    workspaces = [up.workspace for up in UPs if up.workspace.name != Workspace]
    print()
    workspace = Workspace.objects.get(name=workspace)
    r = render(request, 'edmin/code/index.html', {'workspace': workspace, 'workspaces': workspaces, 'username': request.user.username})
    return r


@login_required(login_url='http://localhost:5000/kloudak/index/')
def vms(request, workspace):
    return HttpResponse(f'this is vms of ws: {workspace}')


@login_required(login_url='http://localhost:5000/kloudak/index/')
def networks(request, workspace):
    return HttpResponse(f'this is networks ws: {workspace}')

def tasks(request, workspace, state):
    return HttpResponse('tasks')
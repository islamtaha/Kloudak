from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from InventoryAPI.models import Workspace, CustomUser, VMTemplate, VM, Network
# Create your views here.


def index(request):
    if not request.user.is_anonymous:
        return redirect('http://localhost:5000/kloudak/workspaces/')
    r = render(request, 'ui-index.html', {})
    return r



@login_required
def userDahboard(request):
    UPs = CustomUser.objects.all().filter(user=request.user)
    r = render(request, 'user.html', {'profiles': UPs})
    return r


@login_required
def getWS(request, workspace):
    UPs = CustomUser.objects.all().filter(user=request.user)
    workspaces = [up.workspace for up in UPs if up.workspace.name != Workspace]
    workspace = Workspace.objects.get(name=workspace)
    nets = Network.objects.all().filter(owner=workspace)
    vms = VM.objects.all().filter(owner=workspace)
    r = render(request, 'workspace.html', {'workspace': workspace, 'workspaces': workspaces, 'username': request.user.username, 'nets': nets, 'vms': vms})
    return r


def tasks(request, workspace):
    return HttpResponse('tasks')
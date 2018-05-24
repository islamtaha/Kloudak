#!/usr/bin/python3.6
from .models import Workspace, User, CustomUser
from django.http import HttpResponse
from rest_framework import status
import jwt


def UserToWorkspace_validate(myview):
    def wrapper(request):
        if request.user.is_superuser:
            return myview(request)
        name = request.path.split('/')[1]
        try:
            workspace = Workspace.objects.get(name=name)
            profile = CustomUser.objects.get(user=request.user, workspace=workspace)
        except:
            return HttpResponse('wrong workspace!', status=status.HTTP_400_BAD_REQUEST)
        return myview(request)
    return wrapper

def admin_validate(myview):
    def wrapper(request):
        try:
            token = request.META['HTTP_TOKEN']
        except:
            pass
        if request.user.is_superuser:
            return myview(request)
        else:
            if request.method != 'GET':
                return HttpResponse('please use controller api', status=status.HTTP_405_METHOD_NOT_ALLOWED)

def set_token(myview):
    def wrapper(request):
        resp = myview(request)
        if request.user.is_superuser:
            return resp
        userprofiles = CustomUser.objects.all().filter(user=request.user)
        userpermissions = {}
        for up in userprofiles:
            userpermissions[up.workspace.name] = up.as_dict()
        jwt_token = {'token': jwt.encode(userpermissions, "SECRET_KEY", algorithm='HS256').decode('utf-8')}
        resp['token'] = jwt_token['token']
        return resp
    return wrapper
        
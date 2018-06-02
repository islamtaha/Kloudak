#!/usr/bin/python3.6
from .models import Workspace, User, CustomUser
from django.http import HttpResponse
from rest_framework import status
import jwt


def UserToWorkspace_validate(myview):
    def wrapper(request):
        if request.user.is_superuser:
            return myview(request)
        name = request.path.split('/')[2]
        try:
            workspace = Workspace.objects.get(name=name)
            profile = CustomUser.objects.get(user=request.user, workspace=workspace)
        except Exception as e:
            return HttpResponse('wrong workspace!', status=status.HTTP_400_BAD_REQUEST)
        return myview(request)
    return wrapper

def admin_validate(myview):
    def wrapper(request):
        if request.user.is_superuser:
            return myview(request)
        try:
            token = request.META['HTTP_TOKEN']
            token_dict = jwt.decode(token.encode('utf-8'), "SECRET_KEY", algorithm='HS256')
            username = token_dict['username']
            user = User.objects.get(username=username)
            if user.is_superuser:
                return myview(request)
        except Exception as e:
            if not request.user.is_anonymous:
                pass
            else:
                return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
        if request.method != 'GET':
            return HttpResponse('please use controller api', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            name = request.path.split('/')[1]
        try:
            workspace = Workspace.objects.get(name=name)
            profile = CustomUser.objects.get(user=request.user, workspace=workspace)
        except Exception as e:
            return HttpResponse('wrong workspace!', status=status.HTTP_400_BAD_REQUEST)
        return myview(request)
    return wrapper


def set_token(myview):
    def wrapper(request):
        resp = myview(request)
        if not request.user.is_anonymous:
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
        
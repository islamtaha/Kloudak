
from UI import views
from django.conf.urls import url
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('index/', views.index, name='ui index'),
    path('dashboard/', views.userDahboard, name='user dashboard'),
    path('workspaces/<workspace>/', views.getWS, name='ws dashboard'),
    path('workspaces/<workspace>/tasks/', views.tasks, name='tasks'),
]

from Dashboard import views
from django.conf.urls import url
from django.contrib import admin
from django.urls import path


urlpatterns = [
    path('index/', views.index, name='kloudak index'),
    path('workspaces/', views.workspaces, name='workspaces'),
    path('workspaces/<workspace>/', views.getWS, name='ws dashboard'),
    path('workspaces/<workspace>/vms/', views.vms, name='wsVMs'),
    path('workspaces/<workspace>/networks/', views.networks, name='wsNetworks'),
]
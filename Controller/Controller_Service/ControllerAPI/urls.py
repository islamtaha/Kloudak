from ControllerAPI import views
from django.conf.urls import url
from django.contrib import admin

'''
--------------        API v1.0      --------------
'''

urlpatterns = [
    url(r'^vms/$', views.vms),
    url(r'^networks/$', views.networks),
    url(r'^routers/$', views.routers),
    url(r'^interfaces/$', views.interfaces),
    url(r'^running_tasks/.*/$', views.running_tasks),
    url(r'^finished_tasks/.*/$', views.finished_tasks),
    url(r'^tasks/.*/$', views.tasks),
]

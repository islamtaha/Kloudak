
from InventoryAPI import views
from django.conf.urls import url
from django.contrib import admin


'''
--------------        API v1.0      --------------
'''


urlpatterns = [
    url(r'^get_token/$', views.get_token),
    url(r'^signup/$', views.signup),
    url(r'^login/$', views.userlogin),
    url(r'^logout/$', views.userlogout),
    url(r'^.*/users/$', views.UserProfiles),
    url(r'^.*/users/.*/$', views.UserProfile_Details),
    url(r'^.*/vms/$', views.vms),
    url(r'^.*/vms/.*/$', views.vm_details),
    url(r'^.*/networks/$', views.networks),
    url(r'^.*/networks/.*/$', views.network_details),
    url(r'^areas/$', views.areas),
    url(r'^areas/.*/$', views.area_details),
    url(r'^address/.*/ip/$', views.area_get_ip),
    url(r'^templates/$', views.templates),
    url(r'^templates/.*/$', views.template_details),
    url(r'^workspaces/$', views.workspace),
    url(r'^workspaces/.*/$', views.workspace_details),
    url(r'^.*/routers/$', views.routers),
    url(r'^.*/routers/.*/interfaces/$', views.interfaces),
    url(r'^.*/routers/.*/interfaces/.*/$', views.interface_details),
    url(r'^.*/routers/.*/$', views.router_details)
]


from django.contrib import admin
from .models import networkTask, vmTask, routerTask, interfaceTask
# Register your models here.
admin.site.register(vmTask)
admin.site.register(networkTask)
admin.site.register(routerTask)
admin.site.register(interfaceTask)
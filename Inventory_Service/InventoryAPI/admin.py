
from django.contrib import admin
from .models import VM, Network, Area, VMTemplate, FreeIP, Workspace, RouterInterface, Router
# Register your models here.
admin.site.register(VM)
admin.site.register(Network)
admin.site.register(Area)
admin.site.register(VMTemplate)
admin.site.register(FreeIP)
admin.site.register(Workspace)
admin.site.register(RouterInterface)
admin.site.register(Router)
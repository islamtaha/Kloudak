from django.db import models
from django.utils import timezone
import json
# Create your models here.


class networkTask(models.Model):
    methods = (('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'))
    owner = models.CharField(max_length=200)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    objectName = models.CharField(max_length=200)
    method = models.CharField(max_length=20, choices=methods)
    task = models.TextField()
    username = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(networkTask, self).save(*args, **kwargs)

    def as_dict(self):
        actions = {"POST": "create", "PUT": "update", "DELETE": "delete"}
        return {
            "owner": self.owner,
            "time": self.created,
            "name": self.objectName,
            "action": actions[self.method],
            "type": "network"
        }


class vmTask(models.Model):
    methods = (('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'))
    owner = models.CharField(max_length=200)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    netConf = models.BooleanField(default=False)
    vmConf = models.BooleanField(default=False)
    objectName = models.CharField(max_length=200)
    method = models.CharField(max_length=20, choices=methods)
    task = models.TextField()
    username = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(vmTask, self).save(*args, **kwargs)

    def as_dict(self):
        actions = {"POST": "create", "PUT": "update", "DELETE": "delete"}
        return {
            "owner": self.owner,
            "time": str(self.created),
            "name": self.objectName,
            "action": actions[self.method],
            "type": "vm"
        }


class routerTask(models.Model):
    methods = (('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'))
    owner = models.CharField(max_length=200)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    objectName = models.CharField(max_length=200)
    method = models.CharField(max_length=20, choices=methods)
    task = models.TextField()
    username = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(routerTask, self).save(*args, **kwargs)

    def as_dict(self):
        actions = {"POST": "create", "PUT": "update", "DELETE": "delete"}
        return {
            "owner": self.owner,
            "time": str(self.created),
            "name": self.objectName,
            "action": actions[self.method],
            "type": "router"
        }


class interfaceTask(models.Model):
    methods = (('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE'))
    owner = models.CharField(max_length=200)
    finished = models.BooleanField(default=False)
    created = models.DateTimeField()
    modified = models.DateTimeField()
    objectNetwork = models.CharField(max_length=200)
    method = models.CharField(max_length=20, choices=methods)
    task = models.TextField()
    username = models.CharField(max_length=200)

    def save(self, *args, **kwargs):
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(interfaceTask, self).save(*args, **kwargs)

    def as_dict(self):
        router = json.loads(self.task)["router"]
        actions = {"POST": "create", "PUT": "update", "DELETE": "delete"}
        return {
            "owner": self.owner,
            "time": str(self.created),
            "router": router,
            "network": self.objectNetwork,
            "action": actions[self.method],
            "type": "interface"
        }
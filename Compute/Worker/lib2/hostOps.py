#!/usr/bin/python3.6

from .base import item, dbIO, database
from .orm_schema import Area, Host
from .computeOps import vm
from .exceptions import CreateHostException, DeleteHostException, UpdateHostException
#from .areaOps import area
import libvirt


class host(item):
    def __init__(self, name='', ip='', cpus=0, memory=0, free_memory=0, p_area=None, state=False):
        self.name = name
        self.ip = ip
        self.cpus = cpus
        self.memory = memory
        self.free_memory = free_memory
        self.p_area = p_area
        self.state = state
    
    @classmethod
    def get(cls, name, p_area):
        io = dbIO(database)
        a = io.query(Area, area_name=p_area.name)[0]
        q = io.query(Host, host_name=name, area_id=a.area_id)
        if len(q) == 0:
            return None
        h = q[0]
        return cls(
            name=h.host_name,
            ip=h.host_ip,
            cpus=h.host_cpus,
            memory=h.host_memory,
            free_memory=h.host_free_memory,
            state=h.state,
            p_area=p_area
        )

    def create(self):
        if self.name == '':
            raise CreateHostException('must pass name to class constructor')
        if self.ip == '':
            raise CreateHostException('must pass ip to class constructor')
        if self.p_area == None:
            raise CreateHostException('must pass p_area to class constructor')
        self._prepare_host(self.ip)
        specs = self._get_host_specs(self.ip)
        self.cpus = specs['cpus']
        self.memory = specs['memory']
        self.free_memory = specs['free_memory']
        self.state=True
        io = dbIO(database)
        a = io.query(Area, area_name=self.p_area.name)[0]
        h = Host(
            host_name=self.name,
            host_ip=self.ip,
            host_cpus=self.cpus,
            host_memory=self.memory,
            host_free_memory=self.free_memory,
            area_id=a.area_id,
            state=self.state
        )
        io.add([h])

    def delete(self):
        io = dbIO(database)
        a = io.query(Area, area_name=self.p_area.name)[0]
        h = io.query(Host, host_name=self.name, host_ip=self.ip, area_id=a.area_id)[0]
        io.delete([h])

    def update(self, **kwargs):
        '''name, ip, memory, cpu, free_memory, state, p_area'''
        update_dict={}
        io = dbIO(database)
        old_name = self.name
        old_ip = self.ip
        if 'name' in kwargs:
            update_dict['host_name'] = kwargs['name']
            self.name = kwargs['name']
        if 'ip' in kwargs:
            update_dict['host_ip'] = kwargs['ip']
            self.ip = kwargs['ip']
        if 'memory' in kwargs:
            update_dict['host_memory'] = kwargs['memory']
            self.memory = kwargs['memory']
        if 'free_memory' in kwargs:
            update_dict['host_free_memory'] = kwargs['free_memory']
            self.free_memory = kwargs['free_memory']
        if 'state' in kwargs:
            update_dict['state'] = kwargs['state']
            self.state = kwargs['state']
        if 'p_area' in kwargs:
            a = io.query(Area, area_name=kwargs['p_area'].name)[0]
            update_dict['area_id'] = a.area_id
            self.p_area = kwargs['p_area']
        h = io.query(Host, host_name=old_name, host_ip=old_ip)
        io.update(h, update_dict)

    def _get_host_specs(self, ip):
        conn = libvirt.open(f"qemu+ssh://root@{ip}/system")
        nodeinfo = conn.getInfo()
        body = {}
        body['memory'] = nodeinfo[1] / 1024.0
        body['cpus'] = nodeinfo[2]
        body['free_memory'] = conn.getFreeMemory() / (1024.0 * 1024.0 * 1024.0)
        conn.close()
        return body
    
    def _prepare_host(self, ip):
        pass

    def add_pool(self, pname, path, type=''):
        pass

    def remove_pool(self, pname):
        pass

    def create_vm(self, name, owner, cpu, memory, ip, password, template, size, p_pool, networks=[], key=''):
        v = vm(
            name=name, owner=owner, cpus=cpu, memory=memory, p_host=self, p_pool=p_pool, p_area=self.p_area, networks=networks
        )
        v.create(ip, password, size, template, key=key)
        return v
    
    def delete_vm(self):
        pass

    def update_vm(self):
        pass
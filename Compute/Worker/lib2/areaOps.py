#!/usr/bin/python3.6

from .base import item, dbIO, database
from .orm_schema import Area
from .exceptions import CreateAreaException, DeleteAreaException, UpdateAreaException
from .hostOps import host
from .poolOps import pool
from sqlalchemy import create_engine, func
from .orm_schema import Pool, Host
from .orm_schema import VirtualMachine, PublicIface, PrivateIface
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from .rpcClient import HostRpcClient, PoolRpcClient
import json
import time


class area(item):
    def __init__(self, name='', gw=''):
        self.name = name
        self.gw = gw

    @classmethod
    def get(cls, name):
        io = dbIO(database)
        q = io.query(Area, area_name=name)
        if len(q) == 1:
            return cls(name=name, gw=q[0].area_gw)
        else:
            return None

    def create(self):
        if self.name == '':
            raise CreateAreaException('must pass name to class constructor')
        io = dbIO(database)
        a = Area(area_name=self.name, area_gw=self.gw)
        io.add([a])

    def delete(self):
        if self.name == '':
            raise DeleteAreaException('must pass name to class constructor')
        io = dbIO(database)
        a = Area(area_name=self.name, area_gw=self.gw)
        io.delete([a])

    def update(self, new_name):
        if self.name == '':
            raise UpdateAreaException('must pass name to class constructor')
        io = dbIO(database)
        a = Area(area_name=self.name, area_gw=self.gw)
        io.update(a, {'area_name': new_name})

    def create_vm(self, name, owner, cpu, memory, ip, password, template, size, networks=[], key=''):
        p = self._choose_Pool(size)
        h = self._choose_Host(cpu, memory)
        p_pool = pool().get(name=p, p_area=self)
        p_host = host().get(name=h, p_area=self)
        v = p_host.create_vm(name, owner, cpu, memory, ip, password, template, size, p_pool=p_pool, networks=networks)
        return v


    def add_pool(self, name, path, ptype='dir', source_path='', hostname=''):
        p = pool(name, path, p_area=self)
        p.create(ptype, source_path, hostname)

    def remove_pool(self, name):
        p = pool(name, p_area=self)
        p.delete()

    def add_host(self, name, ip):
        h = host(name, ip, p_area=self)
        h.create()

    def remove_host(self, name, ip):
        h = host(name, ip, p_area=self)
        h.delete()

    def _choose_Host(self, cpu, memory):
        host_rpc = HostRpcClient()
        response = host_rpc.call(cpu, memory, self.name) 
        return response

    def _choose_Pool(self, size):
        pool_rpc = PoolRpcClient()
        response = pool_rpc.call(size, self.name)
        return response 

    def failHost(self, hostname):
        io = dbIO(database)
        h = io.query(Host, host_name=hostname)[0]
        vms = io.generatorQuery(VirtualMachine, host_id=h.host_id)
        for vm in vms:
            v = vm().get(name=vm.vm_name, owner=vm.vm_owner)
            h = self._choose_Host(vm.vm_cpu, vm.vm_memory)
            p_host = host().get(name=h, p_area=self)
            v.failHost(p_host)
            time.sleep(3)
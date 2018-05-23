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
        p_pool = pool().get(name=p.pool_name, p_area=self)
        p_host = host().get(name=h.host_name, p_area=self)
        v = p_host.create_vm(name, owner, cpu, memory, ip, password, template, size, p_pool=p_pool)


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
        postgres_db = {'drivername': 'postgres',
               'username': 'comp_admin',
               'password': 'Maglab123!',
               'host': database,
               'port': 5432,
               'database': 'compute'}
        uri = URL(**postgres_db)
        engine = create_engine(uri)
        Session = sessionmaker(bind=engine)
        session = Session()
        io = dbIO(database)
        a = io.query(Area, area_name=self.name)[0]
        m = memory
        q = session.query(Host).filter(Host.host_free_memory>=m, Host.state==True, Host.area_id==a.area_id).all()
        max_m = 0
        max_h = None
        for h in q:
            if h.host_memory >= max_m:
                max_m = h.host_memory
                max_h = h 
        return max_h

    def _choose_Pool(self, size):
        postgres_db = {'drivername': 'postgres',
               'username': 'comp_admin',
               'password': 'Maglab123!',
               'host': database,
               'port': 5432,
               'database': 'compute'}
        uri = URL(**postgres_db)
        engine = create_engine(uri)
        Session = sessionmaker(bind=engine)
        session = Session()
        io = dbIO(database)
        a = io.query(Area, area_name=self.name)[0]
        s = size
        q = session.query(Pool).filter(Pool.pool_free_size>=s, Pool.area_id==a.area_id).all()
        max_s = 0
        max_p = None
        for p in q:
            if p.pool_size >= max_s:
                max_s = p.pool_size
                max_p = p 
        return max_p
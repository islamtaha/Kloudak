#!/usr/bin/python3.6

from sqlalchemy import Table, Column, Integer, String, Float, Boolean, UniqueConstraint, ForeignKey, DateTime, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import MetaData
import datetime
base = declarative_base()


class Area(base):
    __tablename__ = 'areas'

    area_id = Column(Integer(), primary_key=True)
    area_name = Column(String(50), index=True, unique=True, nullable=False)


class Host_Stats(base):
    __tablename__ = 'host_stats'

    host_id = Column(Integer(), primary_key=True)
    host_name = Column(String(100), nullable=False)
    host_cpus = Column(Integer(), nullable=False)
    host_memory = Column(Float(), nullable=False)
    host_free_memory = Column(Float(), nullable=False)
    state = Column(Boolean(), nullable=False, default=False)
    time = Column(DateTime(), default=datetime.datetime.now())

class Pool_Stats(base):
    __tablename__ = 'pool_stats'

    pool_id = Column(Integer(), primary_key=True)
    pool_name = Column(String(50), nullable=False)
    pool_size = Column(Float(), nullable=False)
    pool_free_size = Column(Float(), nullable=False)
    time = Column(DateTime(), default=datetime.datetime.now())


class VirtualMachine_Stats(base):
    __tablename__ = 'vm_stats'
    
    vm_id = Column(Integer(), primary_key=True)
    vm_name = Column(String(50), nullable=False)
    vm_actual_memory = Column(Integer(), nullable=False)
    vm_cpu_time = Column(BigInteger(), nullable=False)
    vm_system_time = Column(BigInteger(), nullable=False)
    vm_user_time = Column(BigInteger(), nullable=False)
    vm_available_memory =Column(Integer(), nullable=False)
    vm_unused_memory =Column(Integer(), nullable=False)
    time = Column(DateTime(), default=datetime.datetime.now())


class Pool(base):
    __tablename__ = 'pools'

    pool_id = Column(Integer(), primary_key=True)
    pool_name = Column(String(50), index=True, nullable=False, unique=True)
    pool_path = Column(String(100), nullable=False)
    pool_size = Column(Float(), nullable=False)
    pool_free_size = Column(Float(), nullable=False)
    area_id = Column(Integer(), ForeignKey('areas.area_id'))


class Host(base):
    __tablename__ = 'hosts'

    host_id = Column(Integer(), primary_key=True)
    host_name = Column(String(100), index=True, nullable=False, unique=True)
    host_ip = Column(String(100), nullable=False,unique=True)
    host_cpus = Column(Integer(), nullable=False)
    host_memory = Column(Float(), nullable=False)
    host_free_memory = Column(Float(), nullable=False)
    state = Column(Boolean(), nullable=False, default=False)
    area_id = Column(Integer(), ForeignKey('areas.area_id'))


class VirtualMachine(base):
    __tablename__ = 'vms'
    
    vm_id = Column(Integer(), primary_key=True)
    vm_name = Column(String(50), index=True, nullable=False, unique=True)
    vm_memory = Column(Integer(), nullable=False)
    vm_cpus = Column(Integer(), nullable=False)
    vm_ip = Column(String(100), nullable=False)
    state = Column(Boolean(), nullable=False, default=False)
    host_id = Column(Integer(), ForeignKey('hosts.host_id'))
#!/usr/bin/python3.6

from sqlalchemy import Table, Column, Integer, String, Float, Boolean, UniqueConstraint, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import MetaData

base = declarative_base()


class Area(base):
    __tablename__ = 'areas'

    area_id = Column(Integer(), primary_key=True)
    area_name = Column(String(50), index=True, unique=True, nullable=False)
    area_gw = Column(String(100), nullable=False)

    def __repr__(self):
        return f"Area(area_id={self.area_id}, area_name='{self.area_name}')"


class Pool(base):
    __tablename__ = 'pools'

    pool_id = Column(Integer(), primary_key=True)
    pool_name = Column(String(50), index=True, nullable=False, unique=True)
    pool_path = Column(String(100), nullable=False)
    pool_size = Column(Float(), nullable=False)
    pool_free_size = Column(Float(), nullable=False)
    area_id = Column(Integer(), ForeignKey('areas.area_id'))
    #area = relationship("Area", backref=backref('pools', order_by=pool_id))

    def __repr__(self):
        return f'''Pool(pool_id={self.pool_id}, pool_name='{self.pool_name}', \
            pool_path='{self.pool_path}', pool_size={self.pool_size}, \
            pool_free_size={self.pool_free_size}, area_id={self.area_id})'''


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
    #area = relationship("Area", backref=backref('hosts', order_by=host_name))
    
    def __repr__(self):
        return f'''Host(host_id={self.host_id}, host_name='{self.host_name}', host_ip={self.host_ip}, host_cpus={self.host_cpus}, host_memory={self.host_memory}, host_free_memory={self.host_free_memory}, state={self.state}, area_id={self.area_id})'''


class VirtualMachine(base):
    __tablename__ = 'vms'
    __table_args__ = (UniqueConstraint('vm_name', 'vm_owner'),)
    
    vm_id = Column(Integer(), primary_key=True)
    vm_name = Column(String(50), index=True, nullable=False)
    vm_owner = Column(String(50), index=True, nullable=False)
    vm_memory = Column(Integer(), nullable=False)
    vm_cpus = Column(Integer(), nullable=False)
    vm_ip = Column(String(100), nullable=False)
    state = Column(Boolean(), nullable=False, default=False)
    host_id = Column(Integer(), ForeignKey('hosts.host_id'))
    #host = relationship('Host', backref=backref('vms', order_by=vm_name))


class PublicIface(base):
    __tablename__ = 'pub_ifaces'
    __table_args__ = (UniqueConstraint('pub_iface_name', 'host_id'),)

    pub_iface_id = Column(Integer(), primary_key=True)
    pub_iface_name = Column(String(20), index=True, nullable=False)
    pub_iface_state = Column(Boolean(), nullable=False, default=False)
    host_id = Column(Integer(), ForeignKey('hosts.host_id'))
    vm_id = Column(Integer(), ForeignKey('vms.vm_id'))
    #host = relationship('Host', backref=backref('hosts', order_by=pub_iface_name))
    #vm = relationship('VirtualMachine', backref=backref('vms', order_by=pub_iface_id))


class PrivateIface(base):
    __tablename__ = 'pvt_ifaces'
    __table_args__ = (UniqueConstraint('pvt_iface_name', 'host_id'),)

    pvt_iface_id = Column(Integer(), primary_key=True)
    pvt_iface_name = Column(String(20), index=True, nullable=False)
    pvt_iface_state = Column(Boolean(), nullable=False, default=False)
    pvt_iface_mac = Column(String(50), nullable=False)
    pvt_iface_network = Column(String(50), nullable=False)
    host_id = Column(Integer(), ForeignKey('hosts.host_id'))
    vm_id = Column(Integer(), ForeignKey('vms.vm_id'))
    #host = relationship('Host', backref=backref('hosts', order_by=pvt_iface_name))
    #vm = relationship('VirtualMachine', backref=backref('vms', order_by=pvt_iface_id))


class Template(base):
    __tablename__ = 'templates'

    template_id = Column(Integer(), primary_key=True)
    template_name = Column(String(50), index=True, nullable=False, unique=True)
    template_path = Column(String(100), nullable=False) #/var/lib/images/Fedora-27-x86-64.raw
    template_ifname = Column(String(10), nullable=False)


class Volume(base):
    __tablename__ = 'volumes'

    volume_id = Column(Integer(), primary_key=True)
    volume_name = Column(String(100), index=True, nullable=False, unique=True)
    size = Column(Integer(), nullable=False)
    vm_id = Column(Integer(), ForeignKey('vms.vm_id'))
    pool_id = Column(Integer(), ForeignKey('pools.pool_id'))
    #vm = relationship('VirtualMachine', backref=backref('vms', order_by=volume_name))
    #pool = relationship('Pool', backref=backref('volumes', order_by=volume_id))
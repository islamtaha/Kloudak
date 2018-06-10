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



class Host(base):
    __tablename__ = 'hosts'

    host_id = Column(Integer(), primary_key=True)
    host_name = Column(String(100), index=True, nullable=False, unique=True)
    host_ip = Column(String(100), nullable=False,unique=True)
    state = Column(Boolean(), nullable=False, default=False)
    area_id = Column(Integer(), ForeignKey('areas.area_id'))


class Vlan(base):
    __tablename__ = 'vlans'

    vlan_id = Column(Integer(), primary_key=True)
    vlan_available = Column(Boolean(), nullable=False, default=True)


class Network(base):
    __tablename__ = 'networks'
    __table_args__ = (UniqueConstraint('network_name', 'network_owner'),)

    network_id = Column(Integer(), primary_key=True)
    network_name = Column(String(50), index=True, nullable=False, unique=True)
    network_owner = Column(String(50), index=True, nullable=False, unique=True)
    vlan_id = Column(Integer(), ForeignKey('vlans.vlan_id'))



class Iface(base):
    __tablename__ = 'ifaces'

    iface_id = Column(Integer(), primary_key=True)
    iface_name = Column(String(50), index=True, nullable=False)
    iface_mac = Column(String(50), index=True, nullable=False)
    network_id = Column(Integer(), ForeignKey('networks.network_id'))
    host_id = Column(Integer, ForeignKey('hosts.host_id'))
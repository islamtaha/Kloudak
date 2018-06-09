#/usr/bin/python3.6

from sqlalchemy import create_engine
from config import get_config
from orm_schema import base, Area, Host, Network, Vlan, Iface
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from orm_io import dbIO

conf_dict = get_config('conf.json')
postgres_db = {'drivername': 'postgres',
               'username': 'net_admin',
               'password': 'Maglab123!',
               'host': conf_dict['database'],
               'port': 5432,
               'database': 'network'}
uri = URL(**postgres_db)
engine = create_engine(uri)
base.metadata.create_all(engine)
print('created schema')

io = dbIO(conf_dict['database'])
vlans = []
for i in range(2,4090):
    vlan = Vlan(vlan_id=i)
    vlans.append(vlan)

io.add(vlans)
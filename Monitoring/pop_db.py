#!/usr/bin/python3.6

from orm_schema import Host, Area, Pool
from orm_io import dbIO

io = dbIO('localhost')
a = Area(
    area_name='Area-01'
)
io.add([a])
a = io.query(Area, area_name='Area-01')[0]
h = Host(
    host_name='localhost',
    host_ip='127.0.0.1',
    host_cpus=8,
    host_memory=16,
    host_free_memory=10,
    state=True,
    area_id=a.area_id
)
io.add([h])
p2 = Pool(
    pool_name='ISOs',
    pool_path='/home/maged/ISOs/',
    pool_size=40,
    pool_free_size=30,
    area_id=a.area_id
)
p1 = Pool(
    pool_name='default',
    pool_path='/home/maged/ISOs/',
    pool_size=40,
    pool_free_size=30,
    area_id=a.area_id
)
io.add([p1, p2])
#!/usr/bin/python3.6

from orm_schema import Host, Area, Pool
from orm_io import dbIO

io = dbIO('localhost')
#a = Area(
#    area_name='Area-01'
#)
#io.add([a])
a = io.query(Area, area_name='Area-01')[0]
h1 = Host(
    host_name='kvm-1',
    host_ip='192.168.1.7',
    host_cpus=2,
    host_memory=8,
    host_free_memory=8,
    state=True,
    area_id=a.area_id
)
h2 = Host(
    host_name='kvm-2',
    host_ip='192.168.1.8',
    host_cpus=2,
    host_memory=8,
    host_free_memory=8,
    state=True,
    area_id=a.area_id
)
io.add([h1, h2])
p1 = Pool(
    pool_name='pool-01',
    pool_path='/var/lib/pool-01/',
    pool_size=20,
    pool_free_size=20,
    area_id=a.area_id
)
io.add([p1])
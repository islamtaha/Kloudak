#!/usr/bin/python3.6
from lib2.orm_schema import Host, Area, Pool, Template
from lib2.base import dbIO
io = dbIO('localhost')
# a = Area(
#     area_name='Area-01',
#     area_gw='10.10.10.1'
# )
# io.add([a])
t = Template(
    template_name='Template-02.raw',
    template_path='/home/maged/ISOs/',
    template_ifname='eth0'
)
io.add([t])
# a = io.query(Area, area_name='Area-01')[0]
# h1 = Host(
#     host_name='localhost',
#     host_ip='127.0.0.1',
#     host_cpus=4,
#     host_memory=16,
#     host_free_memory=10,
#     state=True,
#     area_id=a.area_id
# )
# io.add([h1])
# a = io.query(Area, area_name='Area-01')[0]
# p1 = Pool(
#     pool_name='pool-01',
#     pool_path='/home/maged/ISOs/',
#     pool_size=40,
#     pool_free_size=40,
#     area_id=a.area_id
# )
# io.add([p1])
#t = io.query(Template, template_name='Template-01')[0]
#path = '/home/maged/ISOs/Fedora-Cloud-Base-27-1.6.x86_64.raw'
#io.update(t, {'template_path': path})

# a = io.query(Area, area_name='Area-01')[0]
# h = Host(
#     host_name='localhost',
#     host_ip='127.0.0.1',
#     host_cpus=8,
#     host_memory=16,
#     host_free_memory=10,
#     state=True,
#     area_id=a.area_id
# )
# io.add([h])
# p2 = Pool(
#     pool_name='ISOs',
#     pool_path='/home/maged/ISOs/',
#     pool_size=40,
#     pool_free_size=30,
#     area_id=a.area_id
# )
# p1 = Pool(
#     pool_name='default',
#     pool_path='/home/maged/ISOs/',
#     pool_size=40,
#     pool_free_size=20,
#     area_id=a.area_id
# )
# io.add([p1, p2])
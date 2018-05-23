#!/usr/bin/python3.6

from lib2 import base
base.database = '127.0.0.1'
from lib2.areaOps import area
from lib2.hostOps import host
from lib2.poolOps import pool
from lib2.computeOps import vm

#p = pool(name='testPool', path='/home/maged/testPool', p_area=area(name='Area-01'))
#p.create()
a = area().get(name='Area-01')
p = pool().get(name='testPool', p_area=area(name='Area-01'))
#print(p.size)
#print(p.free_size)
h = host().get(name='pc.maglab.com', p_area=area(name='Area-01'))
#print(h)
#v = vm(name='VM-01', owner='maged', cpus=1, memory=2, p_pool=p, p_host=h, p_area=a, networks=['Network-01'])
#v.create('192.168.1.1', 'Maglab123!', 10, 'Fedora-Cloud-Base-27-1.6.x86_64.raw')
v = vm().get(name='VM-01', owner='maged', p_area=a)
print(v.network_map)
v.delete()
#h = area(name='Area-01')._choose_Host(2, 1)
#print(h)



#a1 = area().get(name='Area-01')
#print(a1)
#a1.create()
#a2.create()
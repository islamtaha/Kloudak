#/usr/bin/python3.6
from lib.orm_schema import base, Area, Host
from lib.orm_io import dbIO
from config import get_config
conf_dict = get_config('conf.json')
io = dbIO(conf_dict['database'])
a = io.query(Area, area_name='Area-01')[0]
h1 = Host(
    host_name='kvm-1',
    host_ip='192.168.1.7',
    state=True,
    area_id=a.area_id
)
h2 = Host(
    host_name='kvm-2',
    host_ip='192.168.1.8',
    state=True,
    area_id=a.area_id
)
io.add([h1, h2])
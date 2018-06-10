#/usr/bin/python3.6


from orm_schema import base, Area, Host
from orm_io import dbIO
from config import get_config


conf_dict = get_config('conf.json')
io = dbIO(conf_dict['database'])
a = Area(
    area_name='Area-01'
)
io.add([a])
a = io.query(Area, area_name='Area-01')[0]
h = Host(
    host_name='localhost',
    host_ip='127.0.0.1',
    state=True,
    area_id=a.area_id
)
io.add([h])
#!usr/bin/python3.6

import libvirt
from config import get_config
from orm_schema import Area, Host, Pool, VirtualMachine
from orm_schema import Host_Stats, Pool_Stats, VirtualMachine_Stats
from orm_io import dbIO
import datetime
from reporters import host_failure
from threading import Thread


conf_dict = get_config('conf.json')
db = conf_dict['database']
broker = conf_dict['broker']


def dom_log(body):
    io = dbIO(db)
    vm_stat = VirtualMachine_Stats(
        vm_name=body['name'],
        vm_actual_memory=body['memory_stats']['actual'],
        vm_cpu_time=body['cpu_time'],
        vm_system_time=body['system_time'],
        vm_user_time=body['user_time'],
        vm_available_memory=body['memory_stats']['available'],
        vm_unused_memory=body['memory_stats']['unused']
    )
    io.add(objs=[vm_stat])


def host_log(body):
    io=dbIO(db)
    host_stat = Host_Stats(
        host_name=body['name'],
        host_cpus=body['cpus'],
        host_memory=body['memory'],
        host_free_memory=body['free_memory'],
        state=True
    )
    io.add([host_stat])
    hs = io.query(Host, host_name=body['name'])
    if len(hs) == 0:
        hs = io.query(Host, host_ip=body['name'])
    io.update(hs[0], {'host_memory': body['memory'], 'host_free_memory': body['free_memory']})


def pool_log(body):
    io = dbIO(db)
    pool_stat = Pool_Stats(
        pool_name=body['name'],
        pool_size=body['size'],
        pool_free_size=body['free_size']
    )
    io.add([pool_stat])
    p = io.query(Pool, pool_name=body['name'])[0]
    io.update(p, {'pool_size': body['size'], 'pool_free_size': body['free_size']})


def compute_monitor(host):
    io = dbIO(db)
    h = io.query(Host, name=host)[0]
    a = io.query(Area, area_id=h.area_id)[0]
    try:
        conn = libvirt.open(f'qemu+ssh://root@{host}/system')
    except Exception as e:
        host_failure(host, a.area_name, broker)
        io.update(h, {'state': False})
        host_stat = Host_Stats(
            host_name=host,
            host_cpus=h.host_cpus,
            host_memory=h.host_memory,
            host_free_memory=h.host_free_memory,
            state=h.state
        )
        io.add([host_stat])
        return 0
    nodeinfo = conn.getInfo()
    host_body = {}
    host_body['name'] = host
    host_body['memory'] = nodeinfo[1] / 1024.0
    host_body['cpus'] = nodeinfo[2]
    host_body['free_memory'] = conn.getFreeMemory() / (1024.0 * 1024.0 * 1024.0)
    host_log(host_body)
    doms = conn.listAllDomains()
    if len(doms) > 0:
        for dom in doms:
            dom_body = {}
            if dom.isActive():
                dom_body['name'] = dom.name()
                stats = dom.getCPUStats(True)
                dom_body['cpu_time'] = stats[0]['cpu_time']
                dom_body['system_time'] = stats[0]['system_time']
                dom_body['user_time'] = stats[0]['user_time']
                dom_body['memory_stats'] = dom.memoryStats()
                dom_log(dom_body)
    conn.close()


def pool_monitor(host):
    conn = libvirt.open(f'qemu+ssh://root@{host}/system')
    pools = conn.listAllStoragePools()
    if len(pools) > 0:
        pool_body = {}
        for pool in pools:
            info = pool.info()
            pool_body['name'] = pool.name()
            pool_body['size'] = info[1] / (1024 * 1024 * 1024)
            pool_body['free_size'] = info[3] / (1024 * 1024 * 1024)
            pool_log(pool_body)
    conn.close()

            


if __name__ == '__main__':
        compute_monitor('localhost')
        pool_monitor('localhost')
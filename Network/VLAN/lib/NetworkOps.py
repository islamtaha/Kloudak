#!/bin/python3.6

from .orm_io import dbIO, dbTransaction
from .orm_schema import Network, Vlan, Host, Iface
import paramiko

database = ''


class Interface:
    def __init__(self, name='', network=None, host='', mac=''):
        self.name = name
        self.network = network
        self.host = host
        self.mac = mac

    def create(self):
        io = dbIO(database)
        n = io.query(Network, network_name=self.network.name, network_owner=self.network.owner)[0]
        h = io.query(Host, host_name=self.host)[0]
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(h.host_ip, username='root')
        cmd1 = f'ovs-vsctl set Port {self.name} tag={n.vlan_id + 1}'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        e = stderr.read()
        if e:
            print(e)
            ssh.close()
            raise Exception(e)
        ssh.close()
        iface = Iface(
            iface_name = self.name,
            iface_mac = self.mac,
            network_id = n.network_id,
            host_id = h.host_id
        )
        io.add([iface])

    @classmethod
    def get(cls, name, network):
        io = dbIO(database)
        n = io.query(Network, network_name=network.name, network_owner=network.owner)[0]
        ifaces = io.query(Iface, iface_name=name, network_id=n.network_id)
        if len(ifaces) == 0:
            return None
        iface = ifaces[0]
        h = io.query(Host, host_id=iface.host_id)[0]
        return cls(
            name,
            network,
            h.host_name,
            iface.iface_mac
        )

    def delete(self):
        io = dbIO(database)
        iface = io.query(Iface, iface_name=self.name, iface_mac=self.mac)[0]
        io.delete([iface])


class network:
    def __init__(self, name='', owner=''):
        self.name = name
        self.owner = owner

    def create(self):
        t = dbTransaction(database)
        g = t.generatorQuery(Vlan, vlan_available=True)
        try:
            vlan = next(g)
        except Exception as e:
            #log error
            raise Exception('no available vids')
        t.update(vlan, {'vlan_available':False})
        n = Network(
            network_name = self.name,
            network_owner = self.owner,
            vlan_id = vlan.vlan_id
        )
        t.add([n])
        t.commit()

    def delete(self):
        t = dbTransaction(database)
        n = t.query(Network, network_name=self.name, network_owner=self.owner)[0]
        vid = n.vlan_id
        vlan = t.query(Vlan, vlan_id=vid)[0]
        t.delete([n]),
        t.update(vlan, {'vlan_available': True})
        t.commit()

    def addInterface(self, name, host, mac):
        i = Interface(name, self, host, mac)
        i.create()
        return i

    @classmethod
    def get(cls, name, owner):
        io = dbIO(database)
        ns = io.query(Network, network_name=name, network_owner=owner)
        if len(ns) == 0:
            return None
        n = ns[0]
        return cls(n.network_name, n.network_owner)
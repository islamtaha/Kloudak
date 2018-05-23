#!/usr/bin/python3.6
import paramiko
from .exceptions import CreateIfaceException, DeleteIfaceException
from .exceptions import GetIfaceMacException, UpdateIfaceException
from .exceptions import ConnectionFailedException, AddToBridgeException
from .exceptions import BringIfaceUpException, DeleteIfaceException
from .base import item, dbIO, database
import uuid
from .orm_schema import PublicIface, PrivateIface, Host, VirtualMachine

class iface(item):
    def __init__(self, p_vm=None, p_host=None):
        self.p_vm = p_vm
        self.p_host = p_host
        self.name = ''
        self.bridge = ''
        self.i = None


    def create(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.p_host.ip, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd1 = f'ip tuntap add {self.name} mode tap'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateIfaceException(error)
        cmd2 = f'ovs-vsctl add-port {self.bridge} {self.name}'
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise AddToBridgeException(error)
        cmd3 = f'ip link set up dev {self.name}'
        stdin, stdout, stderr = ssh.exec_command(cmd3)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise BringIfaceUpException(error)
        ssh.close()

    def delete(self):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.p_host.ip, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd1 = f'ovs-vsctl del-port {self.name}'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise DeleteIfaceException(error)
        cmd2 = f'ip tuntap del {self.name} mode tap'
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise DeleteIfaceException(error)
        ssh.close()



class publicIface(iface):
    def __init__(self, p_vm=None, p_host=None):
        self.name = uuid.uuid3(uuid.NAMESPACE_DNS, p_vm.name).hex[:15].upper()
        self.p_vm = p_vm
        self.p_host = p_host
        self.bridge = 'public-br'

    def create(self):
        super().create()
        io = dbIO(database)
        h = io.query(Host, host_name=self.p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=self.p_vm.name)[0]
        pi = PublicIface(
            pub_iface_name=self.name,
            pub_iface_state=True,
            host_id=h.host_id,
            vm_id=v.vm_id
            )
        io.add([pi])

    def delete(self):
        super().delete()
        io = dbIO(database)
        h = io.query(Host, host_name=self.p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=self.p_vm.name)[0]
        pi = io.query(PublicIface, host_id=h.host_id, vm_id=v.vm_id)[0]
        io.delete([pi])

    @classmethod
    def get(cls, p_vm, p_host):
        io = dbIO(database)
        h = io.query(Host, host_name=p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=p_vm.name)[0]
        q = io.query(PublicIface, host_id=h.host_id, vm_id=v.vm_id)
        if len(q) == 0:
            return None
        return cls(p_vm, p_host)


class privateIface(iface):
    def __init__(self, p_vm=None, p_host=None, network='', mac=''):
        if p_vm:
            self.name = uuid.uuid3(uuid.NAMESPACE_DNS, f"{p_vm.name}-{network}").hex[:15].upper()
        self.p_vm = p_vm
        self.p_host = p_host
        self.network = network
        self.mac = mac
        self.bridge = 'private-br'

    def create(self):
        super().create()
        io = dbIO(database)
        h = io.query(Host, host_name=self.p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=self.p_vm.name)[0]
        pvi = PrivateIface(
            pvt_iface_name=self.name,
            pvt_iface_network=self.network,
            pvt_iface_mac=self.mac,
            pvt_iface_state=True,
            host_id=h.host_id,
            vm_id=v.vm_id
            )
        io.add([pvi])

    def delete(self):
        super().delete()
        io = dbIO(database)
        h = io.query(Host, host_name=self.p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=self.p_vm.name)[0]
        pvi = io.query(PrivateIface, pvt_iface_name=self.name, host_id=h.host_id, vm_id=v.vm_id)[0]
        io.delete([pvi])

    def update(self, network):
        io = dbIO(database)
        update_dict = {"pvt_iface_network": network}
        h = io.query(Host, host_name=self.p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=self.p_vm.name)[0]
        pvi = io.query(PrivateIface, pvt_iface_name=self.name, host_id=h.host_id, vm_id=v.vm_id)[0]
        io.update(pvi, update_dict)

    @classmethod
    def get(cls, p_vm, p_host, network):
        io = dbIO(database)
        h = io.query(Host, host_name=p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=p_vm.name)[0]
        q = io.query(
            PrivateIface,
            host_id=h.host_id,
            vm_id=v.vm_id,
            pvt_iface_network=network
            )
        if len(q) == 0:
            return None
        pvi = q[0]
        return cls(p_vm=p_vm, p_host=p_host, network=pvi.pvt_iface_network, mac=pvi.pvt_iface_mac)

    @classmethod
    def getAll(cls, p_vm, p_host):
        io = dbIO(database)
        h = io.query(Host, host_name=p_host.name)[0]
        v = io.query(VirtualMachine, vm_name=p_vm.name)[0]
        q = io.query(PrivateIface, host_id=h.host_id, vm_id=v.vm_id)
        if len(q) == 0:
            return []
        res = []
        for i in q:
            res.append(cls(p_vm, p_host, network=i.pvt_iface_network, mac=i.pvt_iface_mac))
        return res
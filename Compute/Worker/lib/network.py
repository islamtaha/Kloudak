#!/usr/bin/python3.6
import paramiko
from .exceptions import CreateIfaceException, DeleteIfaceException
from .exceptions import AddToBridgeException, ConnectionFailedException
from .exceptions import BringIfaceUpException, GetIfaceMacException

class iface(object):
    def __init__(self, name):
        self.name = name


    def __str__(self):
        return self.name


    def getMAC(self, host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd = f'cat /sys/class/net/{self.name}/address'
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.close()
        ssh.close()
        mac = stdout.read()
        error = stderr.read()
        if error:
            raise GetIfaceMacException(error)
        mac = stdout.read()
        return mac


    def delete(self, host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
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


################################################################################################

class publicIface(iface):
    def __init__(self, name, ip=''):
        self.name = name
        self.ip = ip


    def create(self, host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd1 = f'ip tuntap add {self.name} mode tap'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateIfaceException(error)
        cmd2 = f'ovs-vsctl add-port public-br {self.name}'
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
        return self.name


############################################################################################


class privateIface(iface):
    def __init__(self, name, network):
        self.name = f"{name}-{network}"
        self.network = network


    def create(self, host):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd1 = f'ip tuntap add {self.name} mode tap'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateIfaceException(error)
        cmd2 = f'ovs-vsctl add-port private-br {self.name}'
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
        return self.name
#!/usr/bin/python3.6

import paramiko
from ipaddress import ip_interface
from .exceptions import ConnectionFailedException, CreateMetaDataException
from .exceptions import CreateUserDataException, WrongTypeException
from .exceptions import DeleteMetaDataException, DeleteUserDataException


class metaData(object):
    def __init__(self, instance_id, hostname, ifacename, ip, gw):
        self.path = ''
        i = ip_interface(ip)
        addr = str(i.ip)
        net = str(i.network).split('/')[0]
        mask = str(i.netmask)
        self.conf = f"""instance-id: {instance_id}
local-hostname: {hostname}
network-interfaces: |
  iface {ifacename} inet static
  address {addr}
  network {net}
  netmask {mask}
  gateway {gw}
        """
    
    
    def create(self, host, path):
        self.path = path
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd1 = f'touch {path}/meta-data'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateMetaDataException(f'failed to create meta-data file in path {path}')
        cmd2 = f"""echo "{self.conf}" > {path}/meta-data"""
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateMetaDataException(f'failed to write to meta-data file in path {path}')
        ssh.close()


    def delete(self, host, path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException(f'failed to connect to host {host}')
        cmd1 = f'rm {path}/meta-data -f'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise DeleteMetaDataException(f'failed to delete meta-data file in path {path}')




class userData(object):
    def __init__(self, password, **kwargs):
        self.path = ''
        self.conf = f"""#cloud-config
password: {password} \n"""
        self.conf += """chpasswd: { expire: False }
ssh_pwauth: True \n"""
        if 'key' in kwargs:
            key = kwargs['key']
            self.conf += f"""ssh_authorized_keys:
  - ssh-rsa {key}"""


    def create(self, host, path):
        self.path = path
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd1 = f'touch {path}/user-data'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateUserDataException(f'failed to create user-data file in path {path}')
        cmd2 = f"""echo "{self.conf}" > {path}/user-data"""
        stdin, stdout, stderr = ssh.exec_command(cmd2)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise CreateUserDataException(f'failed to write to user-data file in path {path}')
        ssh.close()

    
    def delete(self, host, path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException(f'failed to connect to host {host}')
        cmd1 = f'rm {path}/user-data -f'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise DeleteUserDataException(f'failed to delete user-data file in path {path}')



class configIso(object):
    def __init__(self, md=None, ud=None):
        self.path = ''
        if not isinstance(md, metaData):
            raise WrongTypeException(f"expected metaData object but got {type(md)}")
        if not isinstance(ud, userData):
            raise WrongTypeException(f"expected userData object but got {type(ud)}")
        self.md = md
        self.ud = ud

    def create(self, host, path):
        self.path = path
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException(f'failed to connect to host {host}')
        cmd1 = f'genisoimage -o {path}/config.iso -volid cidata -joliet -rock {self.ud.path}/user-data {self.md.path}/meta-data'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
        ssh.close()
        self.ud.delete(host, self.ud.path)
        self.md.delete(host, self.md.path)
        return f'{path}'


    def delete(self, host, path):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host, username='root')
        except:
            raise ConnectionFailedException(f'failed to connect to host {host}')
        cmd1 = f'rm {path}/config.iso -f'
        stdin, stdout, stderr = ssh.exec_command(cmd1)
        stdin.close()
        error = stderr.read()
        if error:
            ssh.close()
            raise DeleteUserDataException(f'failed to delete user-data file in path {path}')
        ssh.close()
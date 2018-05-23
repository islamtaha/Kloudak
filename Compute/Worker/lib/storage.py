#!/usr/bin/python3.6

import libvirt
from .exceptions import CreateVolumeException, DeleteVolumeException
from .exceptions import ConnectionFailedException, StoragePoolMissingException
from .exceptions import TemplateMissingException


class storage(object):
    def __init__(self, name, size=0, template='', **kwargs):
        self.name = f'{name}.img'
        self.size = size
        self.tname = template
        self.pname = 'mypool'
        self.path = '/var/images'
        if 'pool' in kwargs:
            self.pname = kwargs['pool']
        if 'path' in kwargs:
            self.path = kwargs['path']


    def create(self, host):
        conn = libvirt.open(f'qemu+ssh://root@{host}/system')
        if not conn:
            raise ConnectionFailedException('failed to connect to host')
        sp = conn.storagePoolLookupByName(self.pname)
        if not sp:
            raise StoragePoolMissingException(f"can't find {self.pname} pool")
        t_vol = sp.storageVolLookupByName(self.tname)
        if not t_vol:
            raise TemplateMissingException(f"can't find template {self.tname}")
        vol_xml = f"""
            <volume>
                <name>{self.name}</name>
                <allocation>0</allocation>
                <capacity unit="G">{self.size}</capacity>
                <target>
                    <path>{self.path}/{self.tname}</path>
                </target>
            </volume>
            """
        vol = sp.createXMLFrom(vol_xml, t_vol, 0)
        if not vol:
            raise CreateVolumeException('failed to create volume')
        conn.close()


    def delete(self, host):
        conn = libvirt.open(f'qemu+ssh://root@{host}/system')
        if not conn:
            raise ConnectionFailedException('failed to connect to host')
        sp = conn.storagePoolLookupByName(self.pname)
        if not sp:
            raise StoragePoolMissingException(f"can't find {self.pname} pool")
        vol = sp.storageVolLookupByName(self.name)
        if not vol:
            raise TemplateMissingException(f"can't find volume {self.name}")
        vol.wipe(0)
        vol.delete(0)
        conn.close
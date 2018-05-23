from .base import item, dbIO, database
from .orm_schema import Template, Volume, VirtualMachine, Pool
#from .poolOps import pool
#from .computeOps import vm
from .exceptions import StoragePoolMissingException, TemplateMissingException
from .exceptions import CreateVolumeException, DeleteVolumeException
from .exceptions import ConnectionFailedException
import libvirt

class volume(item):
    def __init__(self, p_vm=None, p_pool=None, size=0):
        self.name = f"{p_vm.name}-{p_vm.owner}.img"
        self.p_vm = p_vm
        self.p_pool = p_pool
        self.size = size

    def create(self, template, host_ip):
        io = dbIO(database)
        t = io.query(Template, template_name=template)[0]
        con = libvirt.open(f'qemu+ssh://root@{host_ip}/system')
        sp = con.storagePoolLookupByName(self.p_pool.name)
        if not sp:
            raise StoragePoolMissingException(f"can't find {self.p_pool.name} pool")
        t_vol = sp.storageVolLookupByName(t.template_name)
        if not t_vol:
            raise TemplateMissingException(f"can't find template {template}")
        vol_xml = f"""
            <volume>
                <name>{self.name}</name>
                <allocation>0</allocation>
                <capacity unit="G">{self.size}</capacity>
                <target>
                    <path>{t.template_path}</path>
                </target>
            </volume>
            """
        vol = sp.createXMLFrom(vol_xml, t_vol, 0)
        if not vol:
            raise CreateVolumeException('failed to create volume')
        con.close()
        v = io.query(VirtualMachine, vm_name=self.p_vm.name, vm_owner=self.p_vm.owner)[0]
        p = io.query(Pool, pool_name=self.p_pool.name)[0]
        vol = Volume(
            volume_name = self.name,
            size = self.size,
            vm_id = v.vm_id,
            pool_id = p.pool_id
            )
        io.add([vol])
        
    def delete(self, host_ip):
        conn = libvirt.open(f'qemu+ssh://root@{host_ip}/system')
        if not conn:
            raise ConnectionFailedException('failed to connect to host')
        sp = conn.storagePoolLookupByName(self.p_pool.name)
        if not sp:
            raise StoragePoolMissingException(f"can't find {self.p_pool.name} pool")
        vol = sp.storageVolLookupByName(self.name)
        if not vol:
            raise TemplateMissingException(f"can't find volume {self.name}")
        vol.wipe(0)
        vol.delete(0)
        conn.close
        io = dbIO(database)
        v = io.query(Volume, volume_name=self.name)[0]
        io.delete([v])

    @classmethod
    def get(cls, p_vm, p_pool, host_ip):
        vol_name = f"{p_vm.name}-{p_vm.owner}"
        io = dbIO(database)
        q = io.query(Volume, volume_name=vol_name)
        if len(q) == 0:
            return None
        vol = q[0]
        return cls(
            p_vm = p_vm,
            p_pool = p_pool,
            size = vol.size
            )

#!/usr/bin/python3.6

from .base import item, dbIO, database
#from .areaOps import area
from .orm_schema import Area, Pool, Volume, Host
import libvirt
from .exceptions import UpdatePoolException, CreatePoolException, DeletePoolException

class pool(item):
    def __init__(self, name='', path='', size=0, free_size=0, p_area=None):
        self.name = name
        self.path = path
        self.size = size
        self.free_size = free_size
        self.p_area = p_area

    @classmethod
    def get(cls, name, p_area):
        io = dbIO(database)
        a = io.query(Area, area_name=p_area.name)[0]
        p = io.query(Pool, pool_name=name, area_id=a.area_id)
        if len(p) == 0:
            return None
        return cls(
            name=p[0].pool_name,
            path=p[0].pool_path,
            size=p[0].pool_size,
            free_size=p[0].pool_free_size,
            p_area=p_area
            )


    def create(self, ptype='dir', source_path='', hostname=''):
        io = dbIO(database)
        a = io.query(Area, area_name=self.p_area.name)[0]
        hosts = io.query(Host, area_id=a.area_id)
        sp_xml = self._xml_gen(ptype, source_path, hostname)
        for h in hosts:
            con = libvirt.open(f"qemu+ssh://root@{h.host_ip}/system")
            sp = con.storagePoolDefineXML(sp_xml, 0)
            con.close()
        con = libvirt.open(f"qemu+ssh://root@{h.host_ip}/system")
        sp = con.storagePoolLookupByName(self.name)
        sp.create()
        info = sp.info()
        self.size = info[1] / (1024 * 1024 * 1024)
        self.free_size = info[3] / (1024 * 1024 * 1024)
        p = Pool(
            pool_name=self.name,
            pool_path=self.path,
            pool_size=self.size,
            pool_free_size=self.free_size,
            area_id=a.area_id
        )
        io.add([p])
        con.close()

    def add_to_host(self, h=None, ptype='dir', source_path='', hostname=''):
        pass

    def remove_from_host(self, h=None):
        pass

    def delete(self):
        io = dbIO(database)
        a = io.query(Area, area_name=self.p_area.name)[0]
        hosts = io.query(Host, area_id=a.area_id)
        for h in hosts:
            con = libvirt.open(f"qemu+ssh://root@{h.host_ip}/system")
            sp = con.storagePoolLookupByName(self.name)
            sp.undefine()
            con.close()
        p = io.query(Pool, pool_name=self.name, area_id=a.area_id)
        io.delete([p])

    def _xml_gen(self, ptype, source_path='', hostname=''):
        dir_xml = f"""
        <pool type="dir">
            <name>{self.name}</name>
            <target>
                <path>{self.path}</path>
            </target>
        </pool>
        """
        fs_xml = f"""
        <pool type="fs">
            <name>{self.name}</name>
            <source>
                <device path="{source_path}"/>
            </source>
            <target>
                <path>{self.path}</path>
            </target>
        </pool>
        """
        iscsi_xml = f"""2
        <pool type="iscsi">
            <name>{self.name}</name>
            <source>
                <host name="{hostname}"/>
                <device path="{source_path}"/>
            </source>
            <target>
                <path>{self.path}</path>
            </target>
        </pool>
        """
        nfs_xml = f"""
        <pool type="netfs">
            <name>{self.name}</name>
            <source>
                <host name="{hostname}"/>
                <dir path="{source_path}"/>
            <format type='nfs'/>
            </source>
            <target>
                <path>{self.path}</path>
            </target>
        </pool>
        """
        type_dict = {
            'nfs': nfs_xml,
            'iscsi': iscsi_xml,
            'dir': dir_xml
            }
        return type_dict[ptype]
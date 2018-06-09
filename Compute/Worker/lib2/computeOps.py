#!/usr/bin/python3.6

from .base import item, database, dbIO
from .orm_schema import Host, VirtualMachine, Template, Area, Volume, Pool
#from .areaOps import area
#from .poolOps import pool
#from .hostOps import host
from .storageOps import volume
from .networkOps import publicIface, privateIface
from .configOps import userData, metaData, configIso
import paramiko, libvirt
import uuid, random
from .exceptions import ConnectionFailedException
from .exceptions import CreateDirException, DeleteDirException
from .exceptions import CreateVmException



class vm(item):
    def __init__(self, name='', owner='', cpus=0, memory=0, p_pool=None, p_host=None, p_area=None, pi=None, networks=[]):
        self.name = name
        self.owner = owner
        self.cpus = cpus
        self.memory = memory
        self.p_pool = p_pool
        self.p_host = p_host
        self.p_area = p_area
        self.networks = networks
        self.network_map = []
        self.ifaces = []
        self.pi = pi


    def _genXML(self, pi, vol):
        pass


    def _createDir(self, host_ip, path):
        dirName = f'{path}/{self.name}-{self.owner}'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host_ip, username='root')
        except:
            raise ConnectionFailedException('failed to connect to host')
        cmd = f"mkdir {dirName}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.close()
        ssh.close()
        error = stderr.read()
        if error:
            raise CreateDirException(f'failed to create directory. {error}')
        return dirName


    def _deleteDir(self, host_ip, path):
        dirName = f'{path}/{self.name}-{self.owner}'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(host_ip, username='root')
        except Exception as e:
            raise ConnectionFailedException('failed to connect to host')
        cmd = f"rm -rf {dirName}"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.close()
        ssh.close()
        error = stderr.read()
        if error:
            raise CreateDirException(f'failed to delete directory. {error}')
        return dirName

    
    def _genMacAddr(self):
        return "00:%02x:%02x:%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
            )
    
    
    def create(self, ip, password, size, template, **kwargs):
        print('vm create')
        io = dbIO(database)
        a = io.query(Area, area_name=self.p_area.name)[0]
        h = io.query(Host, host_name=self.p_host.name, area_id=a.area_id)[0]
        v = VirtualMachine(
            vm_name=self.name,
            vm_owner=self.owner,
            vm_memory=self.memory,
            vm_cpus=self.cpus,
            vm_ip=ip,
            state=False,
            host_id=h.host_id
        )
        io.add([v])
        try:
            p = self._createDir(self.p_host.ip, self.p_pool.path)
        except Exception as e:
            io.delete([v])
            raise CreateVmException('failed to create directory')
        vol = volume(self, self.p_pool, size=size)
        try:
            vol.create(template, self.p_host.ip)
        except Exception as e:
            io.delete([v])
            self._deleteDir(self.p_host, self.p_pool.path)
            raise CreateVmException('failed to create volume')
        pi = publicIface(self, self.p_host)
        try:
            pi.create()
            self.pi = pi
        except Exception as e:
            self._deleteDir(self.p_host, self.p_pool.path)
            vol.delete(self.p_host.ip)
            io.delete([v])
            raise CreateVmException('failed to create public interface')
        network_XML = ''
        if len(self.networks) > 0:
            for n in self.networks:
                try:
                    m = self._genMacAddr()
                    pvi = privateIface(self, self.p_host, n, m)
                    pvi.create()
                    self.ifaces.append(pvi)
                    map_dict = {}
                    map_dict['name'] = pvi.name
                    map_dict['host'] = self.p_host.ip
                    map_dict['network'] = n
                    map_dict['mac'] = m
                    self.network_map.append(map_dict)
                    network_XML += f'''<interface type="ethernet">
            		<mac address="{m}"/>
            		<target dev="{pvi.name}"/>
            		</interface>'''
                except Exception as e:
                    self._deleteDir(self.p_host.ip, self.p_pool.path)
                    vol.delete(self.p_host.ip)
                    pi.delete()
                    if len(self.ifaces) > 0:
                        for i in self.ifaces:
                            i.delete()
                    io.delete([v])
                    raise CreateVmException('failed to create private interfaces')
        #config.iso
        t = io.query(Template, template_name=template)[0]
        md = metaData(self.name, self.name, t.template_ifname, ip, a.area_gw)
        try:
            md.create(self.p_host.ip, p)
        except Exception as e:
            self._deleteDir(self.p_host.ip, self.p_pool.path)
            vol.delete(self.p_host.ip)
            pi.delete()
            if len(self.ifaces) > 0:
                for i in self.ifaces:
                    i.delete()
            io.delete([v])
            raise CreateVmException('failed to create meta-data')
                    
        ud = userData(password, **kwargs)
        try:
            ud.create(self.p_host.ip, p)
        except Exception as e:
            self._deleteDir(self.p_host.ip, self.p_pool.path)
            vol.delete(self.p_host.ip)
            pi.delete()
            if len(self.ifaces) > 0:
                for i in self.ifaces:
                    i.delete()
            io.delete([v])
            raise CreateVmException('failed to create user-data')
        iso = configIso(md, ud)
        try:
            iso_p = iso.create(self.p_host.ip, p)
        except Exception as e:
            self._deleteDir(self.p_host.ip, self.p_pool.path)
            vol.delete(self.p_host.ip)
            pi.delete()
            if len(self.ifaces) > 0:
                for i in self.ifaces:
                    i.delete()
            io.delete([v])
            raise CreateVmException('failed to create config.iso')
        confISO_XML = f'''<disk type="file" device="cdrom">
        <source file="{iso_p}/config.iso"/>
        <target dev="hdb" bus="ide"/>
        </disk>
		'''
        XMLConf = f'''
		<domain type="kvm">
		<name>{self.name}-{self.owner}</name>
		<memory>{self.memory * 1024 *1024}</memory>
		<currentMemory>{self.memory * 1024 * 1024}</currentMemory>
		<vcpu>{self.cpus}</vcpu>
		<os>
		<type arch="x86_64" machine="pc">hvm</type>
		</os>
		<features>
		<acpi/>
		<apic/>
		<pae/>
		</features>
		<clock offset="localtime"/>
		<on_poweroff>destroy</on_poweroff>
		<on_reboot>destroy</on_reboot>
		<on_crash>destroy</on_crash>
		<devices>
		<disk type="file" device="disk">
		<source file="{self.p_pool.path}/{vol.name}"/>
		<target dev="hda" bus="ide"/>
		</disk>
		{confISO_XML}
		<interface type="ethernet">
		<target dev="{pi.name}"/>
		</interface>
		{network_XML}
		<graphics type="vnc" port="5900" autoport="yes" listen="0.0.0.0"/>
		</devices>
		</domain>
		'''
        try:
            conn = libvirt.open(f"qemu+ssh://root@{self.p_host.ip}/system")
            dom = conn.defineXML(XMLConf)
            dom.create()
        except Exception as e:
            self._deleteDir(self.p_host.ip, self.p_pool.path)
            vol.delete(self.p_host.ip)
            pi.delete()
            if len(self.ifaces) > 0:
                for i in self.ifaces:
                    i.delete()
            iso.delete(self.p_host.ip, p)
            io.delete([v])
            raise CreateVmException('failed to create vm')
        conn.close()
        io.update(v, {'state': True})

    
    @classmethod
    def get(cls, name, owner): #p_area):
        from .areaOps import area
        from .poolOps import pool
        from .hostOps import host
        io = dbIO(database)
        v = io.query(VirtualMachine, vm_name=name, vm_owner=owner)[0]
        h = io.query(Host, host_id=v.host_id)[0]
        a = io.query(Area, area_id=h.area_id)[0]
        vol = io.query(Volume, vm_id=v.vm_id)[0]
        p = io.query(Pool, pool_id=vol.pool_id)[0]
        p_area = area().get(name=a.area_name)
        p_host = host().get(name=h.host_name, p_area=p_area)
        p_pool = pool().get(name=p.pool_name, p_area=p_area)
        res = cls(
            name=name, 
            owner=owner, 
            p_host=p_host,
            p_area=p_area,
            p_pool=p_pool,
            cpus=v.vm_cpus,
            memory=v.vm_memory,
            )
        ifaces = privateIface().getAll(res, p_host)
        pi = publicIface.get(res, p_host)
        res.pi = pi
        res.ifaces = ifaces
        if len(ifaces) > 0:
            for i in ifaces:
                res.networks.append(i.network)
                map_dict = {}
                map_dict['name'] = i.name
                map_dict['network'] = i.network
                map_dict['mac'] = i.mac
                map_dict['host'] = p_host.ip
                res.network_map.append(map_dict)
        return res

    def delete(self):
        con = libvirt.open(f'qemu+ssh://root@{self.p_host.ip}/system')
        dom = con.lookupByName(f'{self.name}-{self.owner}')
        dom.destroy()
        dom.undefine()
        self.pi.delete()
        for i in self.ifaces:
            i.delete()
        v = volume(self, self.p_pool)
        v.delete(self.p_host.ip)
        #configIso().delete(self.p_host.ip, f'{self.p_pool.path}/{self.name}-{self.owner}/')
        io = dbIO(database)
        vm = io.query(VirtualMachine, vm_name=self.name, vm_owner=self.owner)[0]
        io.delete([vm])
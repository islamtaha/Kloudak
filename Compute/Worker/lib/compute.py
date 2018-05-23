import libvirt, paramiko
from .network import publicIface, privateIface
from .storage import storage
from .cloudConfig import metaData, userData, configIso
from .exceptions import WrongTypeException, ConnectionFailedException
from .exceptions import CreateDirException, CreateVmException
import random, uuid


class vm(object):
	def __init__(self, name, owner, pool, id_num, cpu=0, ram=0, **kwargs):
		'''
		- required parameters > name(str), owner(str), pool(str), id_num(int) (used with all methods)
		- optional parameters > cpu(int)core, ram(int)GB, disk(int)GB, networks[] (used when creating a new vm)
		- networks > used when deleting a vm
		'''
		self.name = f'{name}-{owner}'
		self.owner = owner
		self.id_num = id_num
		self.cpu = cpu 
		self.ram = ram * 1024 * 1024
		self.ifaces = []	#list of privateInterfaces of the vm (no real value yet)
		self.pool = pool
		self.v_uuid = uuid.uuid3(uuid.NAMESPACE_DNS, self.name)
		self.network_map = []	#contains mapping of (ifname,mac,host,network,owner) to be sent to Network service
		if 'disk' in kwargs:
			if not isinstance(kwargs['disk'], int):
				raise WrongTypeException(f"expected int for disk but got {type(kwargs['disk'])}")
			self.disk = kwargs['disk']
		if 'networks' in kwargs:
			if not isinstance(kwargs['networks'], list):
				raise WrongTypeException(f'expected a list of network names but got {type(kwargs["networks"])}')
			self. networks = kwargs['networks']

	def _createDir(self, host, path):
		dirName = f'{path}/{self.name}'
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(host, username='root')
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


	def _deleteDir(self, host, path):
		dirName = f'{path}/{self.name}'
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			ssh.connect(host, username='root')
		except:
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

	def _pvtNetConf(self, host):
		for n in self.networks:
			i = privateIface(self.id_num, n)
			i.create(host)
			self.ifaces.append(i)


	def create(self, host, password, ifname, ip, hostname, gw, template, path, key=''):
		'''"path" parameter is the path where the storage pool is mounted ('mypool').
			parameters are:
				- host > ip address (str) with prefix of the host (ex:'192.168.1.50/24')
				- password > password of the cloud image user
				- ifname > name of the public interface in cloud image (ex:eth0 in fedora, ens0p3 in centos7)
				- ip > public ip address (str) of the vm
				- hostname > hostname for the vm
				- gw > ip address (str) of the gateway without prefix (ex:'192.168.1.1')
				- template > name of the cloud image template to be used
				- path > the path where the storage pool is mounted ('mypool')
				- key > public key to be added to trusted keys of the vm (optional)
		'''
		try:
			p = self._createDir(host, path)
		except:
			raise CreateVmException(f'failed to create directory {path}')
		md = metaData(hostname, hostname, ifname, ip, gw)
		try:
			md.create(host, p)
		except:
			raise CreateVmException('failed to create meta-data')
		if key == '':
			ud = userData(password)
		else:
			ud = userData(password, key=key)
		try:
			ud.create(host, p)
		except:
			self._deleteDir(host, path)
			md.delete(host, p)
			raise CreateVmException('failed to create user-data')
		iso = configIso(md, ud)
		try:
			iso.create(host, p)
		except:
			self._deleteDir(host, path)
			ud.delete(host, p)
			md.delete(host, p)
			raise CreateVmException('failed to create config iso')
		strg = storage(self.name, self.disk, template, path=path, pool=self.pool)
		try:
			strg.create(host)
		except:
			iso.delete(host, p)
			self._deleteDir(host, path)
			raise CreateVmException('failed to create storage volume')
		net = publicIface(self.id_num, ip)
		try:
			net.create(host)
		except:
			iso.delete(host, p)
			self._deleteDir(host, path)
			strg.delete(host)
			raise CreateVmException('failed to create public interface')
		network_XML = ''
		if len(self.networks) > 0:
			try:
				for n in self.networks:
					i = privateIface(self.id_num, n)
					iname = i.create(host)
					self.ifaces.append(i)
					net_mac = self._genMacAddr()
					network_XML += f'''<interface type="ethernet">
            		<mac address="{net_mac}"/>
            		<target dev="{self.id_num}-{n}"/>
            		</interface>'''
					self.network_map.append({
						"network": n, 
						"mac": net_mac, 
						"iface": iname, 
						"host": host,
						"owner": self.owner
						})
			except:
				iso.delete(host, p)
				self._deleteDir(host, path)
				strg.delete(host)
				net.delete(host)
				if len(self.ifaces) > 0:
					for i in self.ifaces:
						i.delete(host)
				raise CreateVmException('failed to create private interfaces')
        
		confISO_XML = f'''<disk type="file" device="cdrom">
        <source file="{path}/{self.name}/config.iso"/>
        <target dev="hdb" bus="ide"/>
        </disk>
		'''
		for n in self.networks:
			net_mac = self._genMacAddr()
			network_XML += f'''<interface type="ethernet">
            <mac address="{net_mac}"/>
            <target dev="{self.id_num}-{n}"/>
            </interface>'''
			self.network_map.append({
				"network": n, 
				"mac": net_mac, 
				"iface": f"{self.id_num}-{n}", 
				"host": host,
				"owner": self.owner
				})
		XMLConf = f'''
		<domain type="kvm">
		<name>{self.name}</name>
		<uuid>{str(self.v_uuid)}</uuid>
		<memory>{self.ram}</memory>
		<currentMemory>{self.ram}</currentMemory>
		<vcpu>{self.cpu}</vcpu>
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
		<source file="{path}/{self.name}.img"/>
		<target dev="hda" bus="ide"/>
		</disk>
		{confISO_XML}
		<interface type="ethernet">
		<target dev="{self.id_num}"/>
		</interface>
		{network_XML}
		<graphics type="vnc" port="5900" autoport="yes" listen="0.0.0.0"/>
		</devices>
		</domain>
		'''
		conn = libvirt.open(f'qemu+ssh://root@{host}/system')
		if conn == None:
			iso.delete(host, p)
			self._deleteDir(host, path)
			strg.delete(host)
			net.delete(host)
			for i in self.ifaces:
				i.delete(host)
			raise ConnectionFailedException('failed to connect to host')
		try:
			dom = conn.defineXML(XMLConf)
		except Exception as e:
			iso.delete(host, p)
			self._deleteDir(host, path)
			strg.delete(host)
			net.delete(host)
			for i in self.ifaces:
				i.delete(host)
			conn.close()
			raise CreateVmException('failed to define xml for vm.')
		if dom == None:
			iso.delete(host, p)
			self._deleteDir(host, path)
			strg.delete(host)
			net.delete(host)
			for i in self.ifaces:
				i.delete(host)
			conn.close()
			raise CreateVmException('failed to define xml for vm')
		try:
			if dom.create() < 0:
				iso.delete(host, p)
				self._deleteDir(host, path)
				strg.delete(host)
				net.delete(host)
				for i in self.ifaces:
					i.delete(host)
				dom.undefine()
				conn.close()
				raise CreateVmException('failed to create vm')
		except Exception as e:
			iso.delete(host, p)
			self._deleteDir(host, path)
			strg.delete(host)
			net.delete(host)
			for i in self.ifaces:
				i.delete(host)
			conn.close()
			raise CreateVmException('failed to create vm')
		conn.close()
		return self.v_uuid

	def delete(self, host, path=''):
		'''parameters:
			- host > ip address (str) of the host hypervisor
			- path > path where the storage pool is mounted
		'''
		conn = libvirt.open(f'qemu+ssh://root@{host}/system')
		dom = conn.lookupByName(self.name)
		dom.destroy()
		dom.undefine()
		conn.close()
		self._deleteDir(host, path)
		storage(self.name).delete(host)
		publicIface(self.id_num).delete(host)
		for n in self.networks:
			privateIface(self.id_num, n).delete(host)

	def update(self, host, path, new_name, ram, cpu, new_networks=[]):
		conn = libvirt.open(f'qemu+ssh://{host}/system')
		dom = conn.lookupByName(self.name)
		dom.destroy()
		dom.undefine()
		conn.close()
		for n in self.networks:
			privateIface(self.id_num, n).delete(host)
		self.ifaces = []
		self.networks = []
		self.network_map = []
		network_XML = ''
		for n in new_networks:
			i = privateIface(self.id_num, n)
			iname = i.create(host)
			self.ifaces.append(i)
			self.networks.append(n)
			net_mac = self._genMacAddr()
			network_XML += f'''<interface type="ethernet">
            <mac address="{net_mac}"/>
            <target dev="{self.id_num}-{n}"/>
            </interface>'''
			self.network_map.append({
				"network": n, 
				"mac": net_mac, 
				"iface": iname, 
				"host": host,
				"owner": self.owner
				})
		XMLConf = f'''
		<domain type="kvm">
		<name>{self.name}</name>
		<uuid>{str(self.v_uuid)}</uuid>
		<memory>{self.ram}</memory>
		<currentMemory>{self.ram}</currentMemory>
		<vcpu>{self.cpu}</vcpu>
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
		<source file="{path}/{self.name}.img"/>
		<target dev="hda" bus="ide"/>
		</disk>
		<interface type="ethernet">
		<target dev="{self.id_num}"/>
		</interface>
		{network_XML}
		<graphics type="vnc" port="5900" autoport="yes" listen="0.0.0.0"/>
		</devices>
		</domain>
		'''

		#not yest finished
		pass
		
		


	def poweroff(self, host):
		conn = libvirt.open(f'qemu+ssh://{host}/system')
		dom = conn.lookupByName(self.name)
		dom.destroy()
		conn.close()

	def poweron(self, host):
		conn = libvirt.open(f'qemu+ssh://{host}/system')
		dom = conn.lookupByName(self.name)
		dom.create()
		conn.close()

	def reboot(self, host):
		conn = libvirt.open(f'qemu+ssh://{host}/system')
		dom = conn.lookupByName(self.name)
		dom.reboot()
		conn.close()
	
	def reset(self, host):
		conn = libvirt.open(f'qemu+ssh://{host}/system')
		dom = conn.lookupByName(self.name)
		dom.reset()
		conn.close()

	def shutdown(self, host):
		conn = libvirt.open(f'qemu+ssh://{host}/system')
		dom = conn.lookupByName(self.name)
		dom.shutdown()
		conn.close()
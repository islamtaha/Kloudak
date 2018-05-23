#from lib.compute import vm

#t = 'Fedora-Cloud-Base-27-1.6.x86_64.raw'
#p = '/home/maged/images'
#n = 'DBServer'
#owner = 'TeamCloud'
#networks = ['DMZ']
#pool = 'mypool'
#v = vm(name=n, owner=owner, cpu=1, ram=2, pool=pool, disk=10, networks=networks, id_num=17)
#v.create('127.0.0.1', 'Maglab123!', 'eth0', '192.168.1.6/24', n, '192.168.1.1', t, p)
#print(v.network_map)
#v.delete('127.0.0.1', p)
#!usr/bin/python3.6

import libvirt
import time
from config import get_config
from orm_schema import Area, Host, Pool, VirtualMachine
from orm_schema import Host_Stats, Pool_Stats, VirtualMachine_Stats
from orm_io import dbIO
import datetime
from reporters import host_failure
from threading import Thread
from kazoo.client import KazooClient
from celery import Celery
from tasks import compute_monitor, pool_monitor


conf_dict = get_config('conf.json')
db = conf_dict['database']
broker = conf_dict['broker']
tim = conf_dict['time']

            
def threaded_function():
	leader_name = ""
	my_name = ""			
	
	
	zk = KazooClient(hosts='localhost:2181,localhost:2182,localhost:2183')
	zk.start()
	print("Zoo here!!....")
	zk.ensure_path("/electionpath")
	out = zk.create("/electionpath/ch-", b"child",ephemeral=True, sequence=True)
	path = out.split('/')
	my_name = path[len(path)-1]

	io = dbIO(db)


	while True:
		ch = zk.get_children("/electionpath")
		mn1 = my_name	
		for c in ch:
			if mn1 > c:
				mn1 = c
		
		leader_name = mn1

		if my_name == leader_name:
			ips = io.getAll(Host)
			ip_ind = 0
			while ip_ind < len(ips):
				val = ip_ind
				for ip_index in range(val, val+100):					
					if ip_index >= len(ips):
						ip_ind = ip_index						
						break
					else:
						print("hello there!!!")
						#compute_monitor.delay(ips[ip_index].host_name)
						#pool_monitor.delay(ips[ip_index].host_name)
					ip_ind = ip_index
			print("i am a leader")
		else:
			print("i am a follower")
		time.sleep(tim)

if __name__ == '__main__':
	thread = Thread(target = threaded_function)
	thread.start()
	thread.join()

import lib.NetworkOps
lib.NetworkOps.database = '172.17.0.1'
from lib.NetworkOps import network, Interface

n = network().get(name='Network-01', owner='TestWS')
i = Interface().get(name='7079876136A83EB', network=n)
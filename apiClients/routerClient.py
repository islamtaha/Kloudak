from .base import InventoryObject
from .exceptions import CreateRouterException, GetRouterException, DeleteRouterException, UpdateRouterException
from .exceptions import CreateIfaceException, GetIfaceException, DeleteIfaceException, UpdateIfaceException
from .exceptions import WrongTypeException
import json, requests
from .networkClient import network


class iface(object):
    '''interface to interact with router interface objects
        - helper class to implement router class 
        (it's recommended to interact with interfaces through the actions provided in the 'router' class only)
    '''
    def __init__(self, *args, **kwargs):
        self.network = network()
        self.ip = ''
        self.device = router()
        if 'network' in kwargs:
            if isinstance(kwargs['network'], network):
                self.network = kwargs['network']
            else:
                raise WrongTypeException(f"expected a network object but got {type(kwargs['network'])}")
        if 'ip' in kwargs:
            self.ip = kwargs['ip']
        if 'router' in kwargs:
            if isinstance(kwargs['router'], router):
                self.device = kwargs['router']
            else:
                raise WrongTypeException(f"expexted a router object but got {type(kwargs['router'])}")
    

    def __str__(self):
        return self.network.name


    @classmethod
    def get(cls, inventoryIP, inventoryPort, network, router):
        '''retruns with an object of requested interface if available
        - returns None if no interface matches the specified name
        - raises GetIfaceException
        - example:
            n = network().get('127.0.0.1', '5000', 'Network-01', 'Workspace-01')
            r = router().get('127.0.0.1', '5000', owner='Workspace-01', name='Router-01')
            i = iface().get('127.0.0.1', '5000', network=n, router=r)
        '''
        owner = router.owner
        net = network.name
        rtr = router.name
        inventoryURL = f'http://{inventoryIP}:{inventoryPort}/{owner}/routers/{rtr}/interfaces/{net}/'
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetIfaceException('failed to get interface information')
        
        if res.status_code == 404:
            return None
        if res.status_code == 200:
            res_dict = json.loads(res.text)
            ip = res_dict['ip']
            return cls(network=network, ip=ip, router=router)
        else:
            raise GetIfaceException(
                f'''failed to get interface information.
                response status code={res.status_code}.
                response body = {res.txt}
                '''
            )


    @classmethod
    def getAll(cls, inventoryIP, inventoryPort, router):
        '''return a list of all interfaces in a router
            - raises GetIfaceException
            - example:
                r = router().get('127.0.0.1', '5000', owner='Workspace-01', name='Router-01')
                ilist = iface().getAll('127.0.0.1', '5000', router=r)
        '''
        owner = router.owner
        rtr = router.name
        inventoryURL = f'http://{inventoryIP}:{inventoryPort}/{owner}/routers/{rtr}/interfaces/'
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetIfaceException('failed to get interface information')
        
        if res.status_code == 404:
            return []
        if res.status_code == 200:
            res_dict = json.loads(res.text)
            net_names = res_dict['interfaces']
            networks = [
                network().get(inventoryIP, inventoryPort, owner=owner, name=n['name']) 
                for n in net_names
                ]
            ifaces = [cls().get(inventoryIP, inventoryPort, router=router, network=net) for net in networks]
        return ifaces


    def create(self, controllerIP, controllerPort):
        '''creates a router interface with the information provided in the constructor
            - must initialize the object with network, ip, router parameters
            - raises CreateIfaceException
            - example:
                n = network().get('127.0.0.1', '5000', 'Network-01', 'Workspace-01')
                r = router().get('127.0.0.1', '5000', owner='Workspace-01', name='Router-01')
                i = iface(network=n, router=r, ip='192.168.1.1/24')
                i.create('127.0.0.1', '8000')
        '''
        if not bool(self.ip and self.network.name and self.network.owner and self.device.name and self.device.owner):
            raise CreateIfaceException('you need to pass correct parameters to class constructor')
        controllerURL = f'http://{controllerIP}:{controllerPort}/interfaces/'
        body = {
            'network': self.network.name,
            'router': self.device.name,
            'ip': self.ip,
            'owner': self.device.owner
            }
        try:
            res = requests.post(controllerURL, data=json.dumps(body))
        except:
            raise CreateIfaceException('failed to create interface')
            
        if res.status_code == 409:
            raise CreateIfaceException('there is already an interface on the same network for this router')
        elif res.status_code != 200:
            raise CreateIfaceException(
                f'''failed to create interface.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )
        self.device.ifaces.append(self)

    
    def delete(self, controllerIP, controllerPort):
        '''deletes a router interface object
            - the object must have 'network' and 'router' attributes set with old values before calling delete
            - raises DeleteIfaceException
            - example:
                n = network().get('127.0.0.1', '5000', 'Network-01', 'Workspace-01')
                r = router().get('127.0.0.1', '5000', owner='Workspace-01', name='Router-01')
                i = iface(network=n, router=r, ip='192.168.1.1/24')
                i.delete('127.0.0.1', '8000')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/interfaces/'
        body = {
            'owner': self.device.owner,
            'router': self.device.name,
            'network': self.network.name
        }
        try:
            res = requests.delete(controllerURL, data=json.dumps(body))
        except:
            raise DeleteIfaceException('failed to delete interface')
        
        if res.status_code != 202:
            raise DeleteIfaceException(
                f'''failed to delete interface.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )
        self.device.ifaces.remove(self)


    def update(self, controllerIP, controllerPort, **kwargs):
        '''updates a network object information
            - the object must have 'network' and 'router' attributes set with old values before calling update 
            - pass the parameters you need to change as kwargs to this method with their new values(currently only 'ip')
            - values in the current object are updated with new ones
            - raises UpdateIfaceException
            - example:
                n = network().get('127.0.0.1', '5000', 'Network-01', 'Workspace-01')
                r = router().get('127.0.0.1', '5000', owner='Workspace-01', name='Router-01')
                i = iface().get('127.0.0.1', '5000', network=n, router=r)
                i.update('127.0.0.1', '8000', ip='10.10.10.254/24')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/interfaces/'
        if 'ip' in kwargs:
            new_ip = kwargs['ip']
        else:
            new_ip = self.ip
        update_dict = {'ip': new_ip}
        body = {
            'owner': self.device.owner,
            'router': self.device.name,
            'network': self.network.name,
            'update_dict': update_dict
        }
        try:
            res = requests.put(controllerURL, data=json.dumps(body))
        except:
            raise UpdateIfaceException('failed to update interface')
        
        if res.status_code == 200:
            self.ip = new_ip
        else:
            raise UpdateIfaceException(
                f'''failed to update interface.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )


######################################################################################################
######################################################################################################


class router(InventoryObject):
    '''interface to interact with router objects'''
    def __init__(self, *args, **kwargs):
        '''the class contains three attributes:
            - name > str
            - owner > str
            - ifaces > [] list of interface objects
        '''
        self.name = ''
        self.owner = ''
        self.ifaces = []
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'owner' in kwargs:
            self.owner = kwargs['owner']
        if 'ifaces' in kwargs:
            for i in kwargs['ifaces']:
                if isinstance(i, iface):
                    self.ifaces.append(i)
                else:
                    raise WrongTypeException(f"accepts a list of iface objects only but got {type(i)}")
        

    def __str__(self):
        return self.name


    @classmethod
    def get(cls, inventoryIP, inventoryPort, name, owner):
        '''retruns with an object of requested router if available
        - returns None if no router matches the specified name
        - raises GetRouterException, GetIfaceException
        - example:
            r = router().get('127.0.0.1', '5000', owner='Workspace-01', name='Router-01')
        '''
        inventoryURL = f'http://{inventoryIP}:{inventoryPort}/{owner}/routers/{name}/'
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetRouterException('failed to get router information')
        
        if res.status_code == 404:
            return None
        elif res.status_code == 200:
            rtr = cls(name=name, owner=owner)
            ifaces = iface().getAll(inventoryIP, inventoryPort, router=rtr)
            rtr.ifaces = ifaces
            return rtr
        else:
            raise GetRouterException(
                f'''failed to get router information.
                response status code = {res.status_code}.
                response body = {res.text}
                ''')

        
    @classmethod
    def getAll(cls, inventoryIP, inventoryPort, owner):
        '''returns a list of all routers for a specific owner
            - raises GetRouterException, GetIfaceException
            - example:
                rlist = router().getAll('127.0.0.1', '5000', owner='Workspace-01')
        '''
        inventoryURL = f'http://{inventoryIP}:{inventoryPort}/{owner}/routers/'
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetRouterException('failed to get router information')
        
        if res.status_code == 404:
            return []
        elif res.status_code != 200:
            raise GetRouterException(
                f'''failed to get routers.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )
        res_dict = json.loads(res.text)
        routers = [cls().get(inventoryIP, inventoryPort, owner=owner, name=r['name']) for r in res_dict['routers']]
        return routers


    def create(self, controllerIP, controllerPort):
        controllerURL = f'http://{controllerIP}:{controllerPort}/routers/'
        body = {
            'owner': self.owner,
            'name': self.name
        }
        try:
            res = requests.post(controllerURL, data=json.dumps(body))
        except:
            raise CreateRouterException('failed to create router')
        
        if res.status_code == 409:
            raise CreateRouterException('a router already exists with the same name')
        elif res != 200:
            raise CreateRouterException(
                f'''failed to create router.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )
    

    def delete(self, controllerIP, controllerPort):
        controllerURL = f'http://{controllerIP}:{controllerPort}/routers/'
        body = {'name': self.name, 'owner': self.owner}
        try:
            res = requests.delete(controllerURL, data=json.dumps(body))
        except:
            raise DeleteRouterException('failed to delete router')
        
        if res.status_code != 202:
            raise DeleteRouterException(
                f'''failed to delete router.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )

    
    def update(self, controllerIP, controllerPort, **kwargs):
        controllerURL = f'http://{controllerIP}:{controllerPort}/routers/'
        if 'name' in kwargs:
            new_name = kwargs['name']
        else:
            new_name = self.name
        update_dict = {'name': new_name}
        body= {
            'name': self.name,
            'owner': self.owner,
            'update_dict': update_dict
        }
        try:
            res = requests.put(controllerURL, data=json.dumps(body))
        except:
            raise UpdateRouterException('failed to update router')

        if res.status_code == 200:
            self.name = new_name
        else:
            raise UpdateRouterException(
                f'''failed to update router.
                response status code = {res.status_code}.
                response body = {res.text}
                '''
            )


    def createInterface(self, controllerIP, controllerPort, net, ip):
        if not isinstance(net, network):
            raise WrongTypeException(f"expecting object of class network but got {type(net)}")
        i = iface(network=net, router=self, ip=ip)
        i.create(controllerIP, controllerPort)


    def getInterface(self, net):
        if not isinstance(net, network):
            raise WrongTypeException(f"expecting object of network class but got {type(net)}")
        for i in self.ifaces:
            if i.network == net:
                return i
        return None

    
    def deleteInterface(self, controllerIP, controllerPort, **kwargs):
        if 'interface' in kwargs:
            if isinstance(kwargs['interface'], iface):
                i = kwargs['interface']
            else:
                raise WrongTypeException(f"interface kwarg you passed is not of type iface but {type(kwargs['interface'])}")
        elif 'network' in kwargs:
            if not isinstance(kwargs['network'], network):
                raise WrongTypeException(f"network kwarg you passed is not of type network but {type(kwargs['network'])}")
            else:
                i = self.getInterface(kwargs['network'])
        if i:
            i.delete(controllerIP, controllerPort)
        else:
            raise DeleteIfaceException("interface doesn't exist")

    
    def updateInterface(self, controllerIP, controllerPort, ip, **kwargs):
        if 'interface' in kwargs:
            if isinstance(kwargs['interface'], iface):
                i = kwargs['interface']
            else:
                raise WrongTypeException(f"interface kwarg you passed is not of type iface but {type(kwargs['interface'])}")
        elif 'network' in kwargs:
            if not isinstance(kwargs['network'], network):
                raise WrongTypeException(f"network kwarg you passed is not of type network but {type(kwargs['network'])}")
            else:
                i = self.getInterface(kwargs['network'])
        if i:
            i.update(controllerIP, controllerPort, ip=ip)
        else:
            raise DeleteIfaceException("interface doesn't exist")
from .base import InventoryObject
from .exceptions import CreateVmException, GetVmException, DeleteVmException, UpdateVmException
from .exceptions import WrongTypeException
from .networkClient import network
from .templateClient import template
from .areaClient import area
import requests, json


class vm(InventoryObject):
    '''interface to interact with virtual machine objects'''
    def __init__(self, *args, **kwargs):
        '''can be initialized with the following parameters:
            - owner >> str
            - name >> str
            - description >> str
            - ip >> str
            - state >> str
            - area >> object of area class
            - template >> object of template class
            - networks >> list of network objects
        - raises WrongTypeException
        '''
        self.owner = ''
        self.name = ''
        self.description = ''
        self.ip = ''
        self.state = ''
        self.area = area()
        self.template = template()
        self.networks = []
        if 'owner' in kwargs:
            self.owner = kwargs['owner']
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'description' in kwargs:
            self.description = kwargs['description']
        if 'ip' in kwargs:
            self.ip = kwargs['ip']
        if 'state' in kwargs:
            self.state = kwargs['state']
        if 'area' in kwargs:
            if isinstance(kwargs['area'], area):
                self.area = kwargs['area']
            else:
                raise WrongTypeException(
                    f'''accepts only an instance of 'area' class.
                    but recieved {type(kwargs['area'])}
                    '''
                )
        if 'template' in kwargs:
            if isinstance(kwargs['template'], template):
                self.template = kwargs['template']
            else:
                raise WrongTypeException(
                    f'''accepts only an instance of 'template' class.
                    but recieved {type(kwargs['template'])}
                    '''
                )
        if 'networks' in kwargs:
            for n in kwargs['networks']:
                if isinstance(n, network):
                    self.networks.append(n)
                else:
                    raise WrongTypeException(
                        f'''accepts a list containing instances of 'network' class only.
                        but recieved {type(n)}.
                        '''
                    )


    def __str__(self):
        return self.name

    
    @classmethod
    def get(cls, inventoryIP, inventoryPort, name, owner):
        '''returns an object of the requested vm
            - raises GetVmException
            - returns None if no vms are found
            - example:
                vm1 = vm().get(inv_ip, inv_port, name='VM-01', owner='Workspace-01')
        '''
        vmURL = f'http://{inventoryIP}:{inventoryPort}/{owner}/vms/{name}/'
        try:
            vmres = requests.get(vmURL)
        except Exception as e:
            print(e)
            exit(1)
            raise GetVmException(
                f'''error getting vms.
                ''')
        if vmres.status_code == 200:
            res_dict = json.loads(vmres.text)
            vm_description = res_dict['description']
            vm_ip = res_dict['ip']
            vm_state = res_dict['state']
            vm_area = area().get(inventoryIP, inventoryPort, name=res_dict['area'])
            vm_template = template().get(inventoryIP, inventoryPort, name=res_dict['template'])
            if bool(res_dict['networks'][0]):
                vm_networks = [network().get(inventoryIP, inventoryPort, name=n['name'], owner=owner) for n in res_dict['networks']]
            else:
                vm_networks = []
            return cls(
                name = name,
                owner = owner,
                description = vm_description,
                ip = vm_ip,
                state = vm_state,
                area = vm_area,
                template = vm_template,
                networks = vm_networks
                )
        if vmres.status_code == 404:
            return None
        else:
            raise GetVmException(f'''error getting vms.
                response status code={vmres.status_code}.
                response body={vmres.text}
                ''')


    @classmethod
    def getAll(cls, inventoryIP, inventoryPort, owner):
        '''returns a list of all VMs of a workspace
            - raises GetVmException
            - example:
                vms = vm().getAll('127.0.0.1', '5000', 'Workspace-01')
        '''
        inventoryURL = f'http://{inventoryIP}:{inventoryPort}/{owner}/vms/'
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetVmException('error getting vms')
        if res.status_code == 200:
            res_dict = json.loads(res.text)
            if bool(res_dict['vms'][0]):
                vms = [cls().get(inventoryIP, inventoryPort, name=v['name'], owner=owner) for v in res_dict['vms']]
            else:
                vms = []
            return vms


    def create(self, controllerIP, controllerPort, password):
        '''creates a vm with the information provided in the constructor
            - must initialize the object with name, owner, area, template, networks, password parameters at least
            - raises CreateVmException
            - example:
                n1 = network().get(inv_ip, inv_port, name='Network-01', owner='Workspace-01')
                t1 = template().get(inv_ip, inv_port, name='Template-01')
                a1 = area().get(inv_ip, inv_port, name='Area-01')

                v2 = vm(
                        name='VM-03',
                        owner='Workspace-01',
                        template=t1,
                        area=a1,
                        networks=[n1]
                        )
                v2.create('127.0.0.1', '8000', password='mypassword')
        '''
        if not bool(self.name and self.owner and self.area.name and self.template.name):
            raise CreateVmException('you need to pass correct parameters to class constructor')
        controllerURL = f'http://{controllerIP}:{controllerPort}/vms/'
        print(self.networks)
        body = {
            'name': self.name,
            'owner': self.owner,
            'area': self.area.name,
            'template': self.template.name,
            'networks': [n.name for n in self.networks],
            'password': password,
            'description': self.description
        }
        try:
            res = requests.post(controllerURL, data=json.dumps(body))
        except:
            raise CreateVmException('error creating vm')
        if res.status_code == 409:
            raise CreateVmException('a vm already exists with the same name')
        elif res.status_code == 200:
            res_dict = json.loads(res.text)
            self.ip = res_dict['ip']
            self.state = 'C_D'
        else:
            raise CreateVmException(
                f'''error creating vm.
                response code={res.status}.
                response body={res.text}
                '''
            )


    def delete(self, controllerIP, controllerPort):
        '''deletes a vm object
            - the object must have 'name' and 'owner' attributes set with old values before calling delete
            - raises DeleteVmException
            - example:
                v = vm().get('127.0.0.1', '5000', name='VM-01', owner='Workspace-01')
                v.delete('127.0.0.1', '8000')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/vms/'
        body = {'name': self.name, 'owner': self.owner}
        try:
            res = requests.delete(controllerURL, data=json.dumps(body))
        except:
            raise DeleteVmException('error deleting vm')
        if res.status_code != 202:
            raise DeleteVmException(
                f'''vm deletion failed.
                response code={res.status_code},
                body={res.text}
                '''
            )


    def update(self, controllerIP, controllerPort, **kwargs):
        '''updates a vm object information
            - the object must have all attributes set with old values before calling update 
            - pass the parameters you need to change as kwargs to this method with their new values
            - values in the current object are updated with new ones
            - to update the vm networks pass a list of network object as kwarg 'networks' to this method
            - raises UpdateVmException
            - example:
                v = vm().get('127.0.0.1', '5000', name='VM-01', owner='Workspace-01')
                v.update('127.0.0.1', '8000', name='Web-Server', description='apache')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/vms/'
        if 'name' in kwargs:
            new_name = kwargs['name']
        else:
            new_name = self.name
        if 'description' in kwargs:
            new_description = kwargs['description']
        else:
            new_description = self.description
        nlist = []
        if 'networks' in kwargs:
            new_networks = []
            nlist = kwargs['networks']
            if len(kwargs['networks']):
                for n in kwargs['networks']:
                    if isinstance(n, network):
                        new_networks.append({'name': n.name})
                    else:
                        raise WrongTypeException(
                            f'''accepts a list of network objects only.
                            but received {type(n)}    
                            ''')
            else:
                new_networks.append({})
        else:
            nlist = self.networks
            if len(self.networks) > 0:
                new_networks = [{'name': n.name} for n in self.networks]
            else:
                new_networks = [{}]
        update_dict = {
            'name': new_name,
            'description': new_description,
            'new_networks': new_networks
        }
        
        body = {'name': self.name, 'owner': self.owner, 'update_dict': update_dict}
        try:
            res = requests.put(controllerURL, data=json.dumps(body))
        except:
            raise UpdateVmException('error updating vm')
        
        if res.status_code == 200:
            self.name = new_name
            self.description = new_description
            self.networks = nlist
        else:
            raise UpdateVmException(
                    f'''vm update failed.
                    response code={res.status_code}, 
                    body={res.text}
                    ''')
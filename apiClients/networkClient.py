import requests
import json
from .exceptions import GetNetworkException, CreateNetworkException, UpdateNetworkException, DeleteNetworkException
from .base import InventoryObject



class network(InventoryObject):
    '''interface to interact with area objects stored in inventory
    '''
    def __init__(self, *args, **kwargs):
        self.name = ''
        self.owner = ''
        self.description = ''
        self.state = ''
        if 'name' in kwargs:
            self.name = kwargs['name']
        if 'owner' in kwargs:
            self.owner = kwargs['owner']
        if 'description' in kwargs:
            self.description = kwargs['description']
        if 'state' in kwargs:
            self.state = kwargs['state']


    def __str__(self):
        return self.name
    

    @classmethod
    def get(cls, inventoryIP, inventoryPort, name, owner):
        '''retruns with an object of requested network if available
        - returns None if no network matches the specified name
        - raises GetNetworkException
        - example:
            a = network().get('127.0.0.1', '5000', 'Network-01', 'Workspace-01')
        '''
        inventoryURL = f"http://{inventoryIP}:{inventoryPort}/{owner}/networks/{name}/"
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetNetworkException(f'connection refused')
        if res.status_code == 200:
            res_dict = json.loads(res.text)
            return cls(
                name=res_dict['name'],
                owner=owner,
                description=res_dict['description'],
                state=res_dict['state']
                )
        elif res.status_code == 404:
            return None
        else:
            raise GetNetworkException(f'inventory request returned with status code {res.status_code}')

    
    def create(self, controllerIP, controllerPort):
        '''creates a network with the information provided in the constructor
            - must initialize the object with name, owner parameters at least
            - raises CreateNetworkException
            - example:
                n = network(name='Network-01', owner='Workspace-01', description='DMZ-01')
                n.create('127.0.0.1', '8000')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/networks/'
        if self.name == '':
            raise CreateNetworkException('you must provide name in class constructor')
        if self.owner == '':
            raise CreateNetworkException('you must provide owner in class constructor')
        body = {
            "name": self.name,
            "owner": self.owner,
            "description": self.description
        }
        try:
            req = requests.post(controllerURL, json.dumps(body))
        except:
            raise CreateNetworkException('connection failed')
        
        if req.status_code != 200:
            raise CreateNetworkException(
                f'''network creation failed.
                response code={req.status_code}, 
                body={req.text}'
                ''')
            
    
    def update(self, controllerIP, controllerPort, **kwargs):
        '''updates a network object information
            - the object must have 'name' and 'owner' attributes set with old values before calling update 
            - pass the parameters you need to change as kwargs to this method with their new values
            - values in the current object are updated with new ones
            - raises UpdateNetworkException
            - example:
                network(name='Network-01', owner='Workspace-01').update(
                    '127.0.0.1',
                    '8000'
                    name='Network-02',
                    description='DMZ-01'
                    )
                OR
                n = network().get('127.0.0.1', '5000', name='Network-01', owner='Workspace-01')
                n.update('127.0.0.1', '8000', name='Network-02', description='DMZ-01')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/networks/'
        if self.name == '':
            raise CreateNetworkException('you must provide name in class constructor')
        if self.owner == '':
            raise CreateNetworkException('you must provide owner in class constructor')
        update_dict = {}
        if 'name' in kwargs:
            update_dict['name'] = kwargs['name']
        else:
            update_dict['name'] = self.name
        if 'description' in kwargs:
            update_dict['name'] = kwargs['description']
        else:
            update_dict['name'] = self.description
        
        body = {
            'name': self.name,
            'owner': self.owner,
            'update_dict': update_dict
        }
        try:
            req = requests.put(controllerURL, json.dumps(body))
        except:
            raise UpdateNetworkException('connection failed')

        if req.status_code != 200:
            raise UpdateNetworkException(
                f'''network update failed.
                response code={req.status_code}, 
                body={req.text}
                ''')
        self.name = update_dict['name']
        self.description = update_dict['description']


    def delete(self, controllerIP, controllerPort):
        '''deletes a network object
            - the object must have 'name' and 'owner' attributes set with old values before calling delete
            - raises DeleteNetworkException
            - example:
                n = Network().get('127.0.0.1', '5000', name='Network-01', owner='Workspace-01')
                n.delete('127.0.0.1', '8000')
        '''
        controllerURL = f'http://{controllerIP}:{controllerPort}/networks/'
        if self.name == '':
            raise CreateNetworkException('you must provide name in class constructor')
        if self.owner == '':
            raise CreateNetworkException('you must provide owner in class constructor')
        
        body = {
            'name': self.name,
            'owner': self.owner
            }
        try:
            req = requests.delete(controllerURL, data=json.dumps(body))
        except:
            raise DeleteNetworkException('connection failed')
        if req.status_code != 202:
            raise DeleteNetworkException(
                f'''network deletion failed.
                response code={req.status_code},
                body={req.text}
                '''
            )


    @classmethod
    def getAll(cls, inventoryIP, inventoryPort, owner):
        '''return a list of all networks of a workspace
            - raises GetNetworkException
            - example:
                nlist = network().getall('127.0.0.1', '5000', 'Workspace-01')
        '''
        inventoryURL = f"http://{inventoryIP}:{inventoryPort}/{owner}/networks/"
        try:
            res = requests.get(inventoryURL)
        except:
            raise GetNetworkException(f'connection refused')
        
        res_dict = json.loads(res.text)
        if bool(res_dict['networks'][0]):
            networks = [
                cls().get(inventoryIP, inventoryPort, name=n['name'],owner=owner) 
                for n in res_dict['networks']
                    ]
        else:
            networks = []
        return networks
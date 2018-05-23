#!/usr/bin/python3.6


class InventoryObject():
    '''base class for all inventory objects'''
    def __init__(self):
        pass
    
    @classmethod
    def get(cls, inventoryIP, inventoryPort):
        '''returns object of the InventoryObject'''
        pass
    
    def create(self, controllerIP, controllerPort):
        '''creates InventoryObject(no return)'''
        pass
    
    def delete(self, controllerIP, controllerPort):
        '''deletes InventoryObjects(no return)'''
        pass
    
    def update(self, inventoryIP, controllerPort, **kwargs):
        '''updates InventoryObject and updates values in current object(no return)'''
        pass

    @classmethod
    def getAll(cls, inventoryIP, InventoryPort):
        '''returns a list of objects of InventoryObjects'''
        pass
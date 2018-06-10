#!/bin/python3.6

from orm_io import dbIO
from orm_schema import Network, Vlan

database = ''

class network:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner

    def create(self):
        io = dbIO(database)
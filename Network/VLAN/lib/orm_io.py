#/usr/bin/python3.6

from sqlalchemy import create_engine, func
from .orm_schema import Area, Host, Network, Iface, Vlan
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

database = ''


class dbIO(object):
    '''interface used to interact with database objects'''
    def __init__(self, db_server):
        postgres_db = {'drivername': 'postgres',
               'username': 'net_admin',
               'password': 'Maglab123!',
               'host': db_server,
               'port': 5432,
               'database': 'network'}
        uri = URL(**postgres_db)
        engine = create_engine(uri)
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def query(self, cl, **kwargs):
        '''parameters:
            - cl > class of sqlalchemy orm
            returns a list of objects
            example:
                io = dbIO('127.0.0.1')
                areas = io.query(Area, area_name='Area-01')
        '''
        res = self.session.query(cl).filter_by(**kwargs).all()
        return res

    def generatorQuery(self, cl, **kwargs):
        '''parameters:
            - cl > class of sqlalchemy orm
            retruns a generator
            example:
                io = dbIO('127.0.0.1')
                g = io.generatorQuery(Area)
                a = next(g)
        '''
        for res in self.session.query(cl).filter_by(**kwargs).all():
            yield res

    def add(self, objs=[]):
        '''parameters:
            - objs > a list of the objects to be added
            no return
            example:
                a1 = Area(area_name='Area-01')
                p1 = Pool(pool_name='Pool-01', pool_size=50, pool_free_size=50, pool_area_id=a1.area_id)
                io = dbIO('127.0.0.1')
                io.add([a1, p1])
        '''
        for obj in objs:
            self.session.add(obj)
        self.session.commit()

    def delete(self, objs=[]):
        '''parameters:
            - objs > a list of the objects to be deleted
            no return
        '''
        for obj in objs:
            self.session.delete(obj)
        self.session.commit()

    def update(self, obj, update_dict={}):
        '''parameters:
            - obj > the object to be updated
            - update_dict > dictionary containing pairs of attribute name(str) and new value
            returns modified object
            example:
                io = dbIO('127.0.0.1')
                areas = io.query(Area)
                a = io.update(areas[-1], {'area_name': 'New_Area'})
        '''
        q = self.session.query(type(obj)).all()
        for o in q:
            if obj == o:
                for attr in update_dict:
                    setattr(o, attr, update_dict[attr])
                self.session.commit()
                break
        return o

    def __del__(self):
        self.session.close()





class dbTransaction:
    def __init__(self, db_server):
        postgres_db = {'drivername': 'postgres',
               'username': 'net_admin',
               'password': 'Maglab123!',
               'host': db_server,
               'port': 5432,
               'database': 'network'}
        uri = URL(**postgres_db)
        engine = create_engine(uri)
        Session = sessionmaker(bind=engine)
        self.session = Session()


    def query(self, cl, **kwargs):
        '''parameters:
            - cl > class of sqlalchemy orm
            returns a list of objects
            example:
                t = dbTransaction('127.0.0.1')
                areas = t.query(Area, area_name='Area-01')
        '''
        res = self.session.query(cl).filter_by(**kwargs).all()
        return res


    def generatorQuery(self, cl, **kwargs):
        '''parameters:
            - cl > class of sqlalchemy orm
            retruns a generator
            example:
                t = dbTransaction('127.0.0.1')
                g = t.generatorQuery(Area)
                a = next(g)
        '''
        for res in self.session.query(cl).filter_by(**kwargs).all():
            yield res


    def add(self, objs=[]):
        '''parameters:
            - objs > a list of the objects to be added
            no return
            example:
                a1 = Area(area_name='Area-01')
                p1 = Pool(pool_name='Pool-01', pool_size=50, pool_free_size=50, pool_area_id=a1.area_id)
                t = dbTransaction('127.0.0.1')
                t.add([a1, p1])
                t.commit()
        '''
        for obj in objs:
            self.session.add(obj)


    def delete(self, objs=[]):
        '''parameters:
            - objs > a list of the objects to be deleted
            no return
        '''
        for obj in objs:
            self.session.delete(obj)


    def update(self, obj, update_dict={}):
        '''parameters:
            - obj > the object to be updated
            - update_dict > dictionary containing pairs of attribute name(str) and new value
            returns modified object
            example:
                t = dbTransaction('127.0.0.1')
                areas = t.query(Area)
                a = t.update(areas[-1], {'area_name': 'New_Area'})
                t.commit()
        '''
        q = self.session.query(type(obj)).all()
        for o in q:
            if obj == o:
                for attr in update_dict:
                    setattr(o, attr, update_dict[attr])
                break
        return o

    def commit(self):
        self.session.commit()

    def __del__(self):
        self.session.close()
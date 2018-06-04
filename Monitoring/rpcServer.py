from sqlalchemy import create_engine, func
from orm_schema import Pool, Host, Area
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
from config import get_config
from orm_io import dbIO
import pika, json
from threading import Thread


conf_dict = get_config('conf.json')
db = conf_dict['database']
broker = conf_dict['broker']



def choose_Host(cpu, memory, area):
    postgres_db = {'drivername': 'postgres',
           'username': 'mon_admin',
            'password': 'Maglab123!',
           'host': db,
           'port': 5432,
           'database': 'monitor'}
    uri = URL(**postgres_db)
    engine = create_engine(uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    io = dbIO(db)
    a = io.query(Area, area_name=area)[0]
    m = memory
    q = session.query(Host).filter(Host.host_free_memory>=m, Host.state==True, Host.area_id==a.area_id).all()
    max_m = 0
    max_h = None
    for h in q:
        if h.host_memory >= max_m:
            max_m = h.host_memory
            max_h = h 
    return max_h


def choose_Pool(size, area):
    postgres_db = {'drivername': 'postgres',
            'username': 'mon_admin',
           'password': 'Maglab123!',
           'host': db,
           'port': 5432,
            'database': 'monitor'}
    uri = URL(**postgres_db)
    engine = create_engine(uri)
    Session = sessionmaker(bind=engine)
    session = Session()
    io = dbIO(db)
    a = io.query(Area, area_name=area)[0]
    s = size
    q = session.query(Pool).filter(Pool.pool_free_size>=s, Pool.area_id==a.area_id).all()
    max_s = 0
    max_p = None
    for p in q:
        if p.pool_size >= max_s:
            max_s = p.pool_size
            max_p = p 
    return max_p



def host_request(ch, method, props, body):
    body_dict = json.loads(body.decode('utf-8'))
    h = choose_Host(body_dict['cpu'], body_dict['memory'], body_dict['area'])
    response = {'name': h.host_name, 'ip': h.host_ip}
    jres = json.dumps(response)
    ch.basic_publish(exchange='',
    routing_key=props.reply_to,
    properties=pika.BasicProperties(correlation_id=props.correlation_id),
    body=jres
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def pool_request(ch, method, props, body):
    body_dict = json.loads(body.decode('utf-8'))
    p = choose_Pool(body_dict['size'], body_dict['area'])
    response = {'name': p.pool_name}
    jres = json.dumps(response)
    ch.basic_publish(exchange='',
    routing_key=props.reply_to,
    properties=pika.BasicProperties(correlation_id=props.correlation_id),
    body=jres
    )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def hostThread():
    h_connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    h_channel = h_connection.channel()
    h_channel.queue_declare(queue='host_rpc_queue')
    h_channel.basic_qos(prefetch_count=1)
    h_channel.basic_consume(host_request, queue='host_rpc_queue')
    h_channel.start_consuming()


def poolThread():
    p_connection = pika.BlockingConnection(pika.ConnectionParameters(host=broker))
    p_channel = p_connection.channel()
    p_channel.queue_declare(queue='pool_rpc_queue')
    p_channel.basic_qos(prefetch_count=1)
    p_channel.basic_consume(pool_request, queue='pool_rpc_queue')
    p_channel.start_consuming()


def main():
    hThread = Thread(target=hostThread, daemon=True)
    pThread = Thread(target=poolThread, daemon=True)
    hThread.start()
    pThread.start()
    hThread.join()
    pThread.join()


if __name__ == '__main__':
        main()
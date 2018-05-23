import psycopg2
from config import dbserver

class privateNetwork():
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.error = ''

    def create(self):
        print('creating')
        self.conn = psycopg2.connect(database="network", user="netuser", password="Maglab123!", host=dbserver, port="5432")
        self.cur = self.conn.cursor()
        try:
            q1 = "SELECT MIN(id) FROM vlanStatus WHERE status='available';"
            self.cur.execute(q1)
            vlan_id = self.cur.fetchall()[0][0]
            q2 = f"UPDATE vlanStatus SET status='NA' WHERE id={vlan_id};"
            self.cur.execute(q2)
            q3 = f"INSERT INTO vlans (id, owner, name) VALUES ({vlan_id}, '{self.owner}', '{self.name}');"
            self.cur.execute(q3)
            self.conn.commit()
        except Exception as e:
            self.conn.close()
            self.error = e
            return 1
        print('success creating')
        self.conn.close()
        return 0

    def getID(self):
        self.conn = psycopg2.connect(database="network", user="netuser", password="Maglab123!", host=dbserver, port="5432")
        self.cur = self.conn.cursor()
        q1 = f"SELECT id FROM vlans WHERE name='{self.name}' AND owner='{self.owner}'"
        self.cur.execute(q1)
        try:
            vlan_id = self.cur.fetchall()[0][0]
            self.conn.commit()
        except Exception as e:
            self.conn.close()
            self.error = e
            return None
        self.conn.close()
        return vlan_id

    def delete(self):
        vlan_id = self.getID()
        self.conn = psycopg2.connect(database="network", user="netuser", password="Maglab123!", host=dbserver, port="5432")
        self.cur = self.conn.cursor()
        if vlan_id:
            try:
                q1 = f"DELETE FROM vlans WHERE id={vlan_id}"
                self.cur.execute(q1)
                q2 = f"UPDATE vlanStatus SET status='available' WHERE id={vlan_id}"
                self.cur.execute(q2)
                self.conn.commit()
                self.conn.close()
            except psycopg2.ProgrammingError as exc:
                self.conn.rollback()
            except Exception as e:
                self.error = e
                return 1
            return 0
        return 1
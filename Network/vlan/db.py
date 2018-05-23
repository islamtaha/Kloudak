import psycopg2

conn = psycopg2.connect(database="network", user="netuser",
        password="Maglab123!", host="127.0.0.1", port="5432")

cur = conn.cursor()
for i in range(0, 4095):
        cur.execute(
                f"insert into vlanStatus (id, status) values ({i}, 'available');"
                )

conn.commit()
conn.close()

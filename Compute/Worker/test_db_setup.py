import psycopg2

conn = psycopg2.connect(database="compute", user = "comp_admin", password = "Maglab123!", host = "127.0.0.1", port = "5432")
cur = conn.cursor()

cur.execute('''CREATE TABLE areas
        (area_id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL
        );''')

print("areas Table created successfully")

cur.execute('''CREATE TABLE pools
        (pool_id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        path VARCHAR(100) NOT NULL,
        size REAL NOT NULL,
        free_space REAL NOT NULL,
        FOREIGN KEY (area_id)
        REFERENCES areas (area_id) ON DELETE CASCADE
        );''')

print("pools Table created successfully")

cur.execute('''CREATE TABLE hosts
        (host_name VARCHAR(100) PRIMARY KEY,
        ip VARCHAR(100) NOT NULL,
        cpu INT NOT NULL,
        ram REAL NOT NULL,
        free_ram REAL NOT NULL,
        state BOOLEAN NOT NULL,
        FOREIGN KEY (area_id)
        REFERENCES areas (area_id) ON DELETE CASCADE
        );''')

print("hosts Table created successfully")

cur.execute('''CREATE TABLE vms
        (vm_id SERIAL PRIMARY KEY NOT NULL,
        name VARCHAR(50) NOT NULL,
        owner VARCHAR(50) NOT NULL,
        ram INT NOT NULL,
        cpu INT NOT NULL,
        FOREIGN KEY (host_name)
        REFERENCES hosts (host_name),
        state BOOLEAN NOT NULL
        );''')

print("vms Table created successfully")

cur.execute('''CREATE TABLE public_ifaces
        (public_iface_id SERIAL PRIMARY KEY,
        name VARCHAR(20) NOT NULL,
        ip VARCHAR(100) NOT NULL,
        FOREIGN KEY (vm_id)
        REFERENCES vms (vm_id) ON DELETE CASCADE,
        FOREIGN KEY (host_name)
        REFERENCES hosts (host_name) ON DELETE CASCADE,
        state BOOLEAN NOT NULL
        );''')

print("public_ifaces Table created successfully")

cur.execute('''CREATE TABLE private_ifaces
        (private_iface_id SERIAL PRIMARY KEY;
        name VARCHAR(20) NOT NULL,
        network VARCHAR(50) NOT NULL,
        mac_address VARCHAR(100) NOT NULL,
        FOREIGN KEY (vm_id)
        REFERENCES vms (vm_id) ON DELETE CASCADE,
        FOREIGN KEY (host_name)
        REFERENCES hosts (host_name) ON DELETE CASCADE
        );''')

print("private_ifaces Table created successfully")

cur.execute('''CREATE TABLE templates
        (template_name VARCHAR(100) PRIMARY KEY,
        path VARCHAR(100) NOT NULL
        );''')

print("templates Table created successfully")

cur.execute('''CREATE TABLE volumes
        (volume_id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        size INT NOT NULL,
        FOREIGN KEY (vm_id)
        REFERENCES vms (vm_id) ON DELETE CASCADE,
        FOREIGN KEY (template_name)
        REFERENCES templates (template_name),
        FOREIGN KEY (pool_id)
        REFERENCES pools (pool_id)
        );''')

conn.commit()
conn.close()

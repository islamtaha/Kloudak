import paramiko

class VLANConf():
    def __init__(self, iface, vlan_id, host, user='root', pw='Maglab123!', key_path='/home/maged/.ssh/id_rsa.pub'):
        self.iface = iface
        self.vlan_id = vlan_id
        self.host = host
        self.user = user
        self.pw = pw
        self.key_filename = key_path

    def add(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, username=self.user, password=self.pw, key_filename=self.key_filename)
        cmd = f'ovs-vsctl set port {self.iface} tag={self.vlan_id}'
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        stdin.close()
        self.error = stderr.read()
        if self.error:
            self.ssh.close()
            return None
        self.ssh.close()
        return 0

    def __del__(self):
        self.ssh.close()
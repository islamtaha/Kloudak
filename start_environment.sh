#!/bin/bash
#set -e
echo "Prepring Network..."
sudo ip address add 20.20.20.2/24 dev hypervisor-mgmt
sudo ip tuntap add dev router-internal mode tap
sudo ovs-vsctl add-port hypervisor-pub router-internal
sudo ifconfig router-internal up
sudo ip tuntap add dev kvm1-pub mode tap
sudo ip tuntap add dev kvm2-pub mode tap
sudo ovs-vsctl add-port hypervisor-pub kvm1-pub
sudo ovs-vsctl add-port hypervisor-pub kvm2-pub
sudo ifconfig kvm1-pub up
sudo ifconfig kvm2-pub up
sudo ip tuntap add dev kvm1-mgmt mode tap
sudo ip tuntap add dev kvm2-mgmt mode tap
sudo ovs-vsctl add-port hypervisor-mgmt kvm1-mgmt
sudo ovs-vsctl add-port hypervisor-mgmt kvm2-mgmt
sudo ifconfig kvm1-mgmt up
sudo ifconfig kvm2-mgmt up
sudo ip tuntap add dev kvm1-pvt mode tap
sudo ip tuntap add dev kvm2-pvt mode tap
sudo ovs-vsctl add-port hypervisor-pvt kvm1-pvt
sudo ovs-vsctl add-port hypervisor-pvt kvm2-pvt
sudo ifconfig kvm1-pvt up
sudo ifconfig kvm2-pvt up
#echo "Starting Router..."
#sudo virsh start router
#sleep 1m
#echo "Starting RabbitMQ..."
#docker start kloudak-rabbitmq
#echo "Starting PostgreSQL..."
#docker start kloudak-postgres
#echo "Starting Inventory..."
#docker start kloudak-inventory
#echo "Starting Controller..."
#docker start kloudak-controller
#echo "Starting NFS Server..."
#sudo virsh start nfs-server
#sleep 1m
#echo "Starting Hypervisors..."
#sudo virsh start kvm1
#sleep 1m
#sudo virsh start kvm2
#sleep 1m
#echo "Starting Compute..."
#docker start kloudak-compute
#echo "Starting Network..."
#docker start kloudak-network
#echo "Starting Monitor..."
#docker start kloudak-monitor
#echo "Starting Notification..."
#docker start kloudak-notification
#echo "Starting Dashboard"
#docker start kloudak-dashboard
#echo "Kloudak Started!"
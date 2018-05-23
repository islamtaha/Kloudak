from netfilterqueue import NetfilterQueue

def print_and_accept(pkt):
    print(pkt)
    payload = pkt.get_payload()
    print ("-----payload is >>")
    print(payload)
    mac = pkt.get_hw()
    print("MAC Address is >> %s", mac)
    pkt.accept()

nfqueue = NetfilterQueue()
nfqueue.bind(1, print_and_accept)
nfqueue.run()
nfqueue.unbind()

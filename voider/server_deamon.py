import urllib.request
import os
import paramiko
import time
import socket
import subprocess
import mymodule
import re
from pathlib import Path
import threading

def udp_punch(access, self, localpath, idx):
    
    vps_ip = access[0][1:]
    username = access[1][1:]
    password = access[2][1:]
    client = access[5][1:]
    vps_port = access[6][1:]
    local_port = 9866 + idx
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', local_port))
    addr = (vps_ip, vps_port)
    message = b'\'' + self + ' ' + client

    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-p", "UDP", "--dport", local_port, "-j", "REDIRECT", "--to-port", "1194"])

    while True :
        if mymodule.isAlive(vps_ip, username, password, client, localpath):

            threading.Thread(target=mymodule.send, args=(sock, addr, message, )).start()

            data, addr = sock.recvfrom(1024)
            print('client received from vps : {} {}'.format(addr, data))
            temp = msg_to_addr_and_pair(data)
            addr = (temp[0], temp[1])
            pair = [temp[2], temp[3]]
    
            print(pair[0] + ' ' + pair[1])

            if pair[0] == client and pair[1] == self:
                ended = True
                sock.sendto(message, addr)

                data, addr = sock.recvfrom(1024)
                print('punch received: {} {}'.format(addr, data))
    
                sock.sendto(message, addr)

                data, addr = sock.recvfrom(1024)
                print('punch received: {} {}'.format(addr, data))

                sock.close()                
                
                time.sleep(10)
                
                if mymodule.ping2('172.31.0.' + idx):
                    connected = True
                
                first = True
                count = 0
                while connected :
                    if mymodule.ping2('172.31.0.' + idx) :
                        print("ping succeeded")
                        count = 0
                        time.sleep(15)
                    else :
                        if count == 3 :
                            connected = False
                        print("ping failed")
                        time.sleep(5)
                        count = count + 1

def connect_to_clients():
    
    localpath = home + '/.config/voider/self/'
    with open("creds") as file:
        self = file.read().splitlines()[5][1:]
    file.close()

    with open("occupants") as file:
        clients = file.read().splitlines()
    file.close()

    idx = 1
    for client in clients :
        idx = idx + 1
        if client[0] == '1'
            cred = client[2:]
            with open(localpath + 'client_creds/' + cred + '/' + cred) as file:
                access = file.read().splitlines()
            file.close()

            temp = localpath + 'client_creds/' + cred
            
            threading.Thread(target=udp_punch, args=(access, self, temp, idx,  )).start()


home = str(Path.home())

os.chdir("/etc/openvpn/ccd")

n = len([name for name in os.listdir('.') if os.path.isfile(name)])

print(n)

# place the needed nat rules 

subprocess.run(["iptables", "-t", "nat", "--flush"])

subprocess.run(["ip", "addr", "add", "172.16.1.6/30", "dev", mymodule.getint_in( home + '/.config/voider/self' )])

subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out( home + '/.config/voider/self' ), "-j", "MASQUERADE"])


# into the tunnel :
subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.16.1.5", "-j", "SNAT", "--to-source", "172.29.1.1"])
# out of the tunnel :
subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "all", "-j", "DNAT", "--to-destination", "172.16.1.5"])

m1 = []
m2 = []
for x in range(1, n+1):

    callee1 = '10.1.'+ str(x + 1) +'.1'
    callee2 = '172.29.'+ str(x + 1) + '.1'
# into the tunnel :
    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in( home + '/.config/voider/self' ), "-d", callee1, "-p", "all", "-j", "DNAT", "--to-destination", callee2])
# out of the tunnel :
    subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_in( home + '/.config/voider/self' ), "-s", callee2, "-p", "all", "-j", "SNAT", "--to-source", callee1])
    m1.append(callee1)
    m2.append(callee2)


threading.Thread(target=mymodule.patch, args=(home, m1, m2, )).start()

threading.Thread(target=connect_to_clients, args=()).start()


localpath = home + '/.config/voider/self/'

os.chdir(localpath)

with open("creds") as file:
    L = file.read().splitlines()
    host = L[0][1:]
    username = L[3][1:]
    password = L[4][1:]
    server = L[5][1:]
file.close()

localpath = home + '/.config/voider/self/DoA'
remotepath = '/' + server + '/DoA'
while(True):

    Upload(username, password, localpath, remotepath, host)
            
    time.sleep(60)


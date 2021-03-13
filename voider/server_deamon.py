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
import concurrent.futures


def udp_punch(access, self, client, localpath, idx, home):
    
    vps_ip = access[0][1:]
    username = access[1][1:]
    password = access[2][1:]
    folder = access[3][1:]
    vps_port = access[4][1:]
        
    address = (vps_ip, int(vps_port))
    
    while True :
        if mymodule.isAlive(vps_ip, username, password, localpath):
            print("isAlive")
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 0))
            local_port = sock.getsockname()[1]
            sock.settimeout(20)
            e1 = threading.Event()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.submit(mymodule.send, sock, address, self, client, e1, 3, 5)
                future = executor.submit(mymodule.receive_meeting_port, sock, e1, home)
                result1 = future.result()
                if result1[0] :
                    sock.settimeout(120)
                    address2 = result1[1]
                    e2 = threading.Event()
                   
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        executor.submit(mymodule.send, sock, address2, self, client, e2, 12, 10)
                        future = executor.submit(mymodule.receive_server, sock, self, client, e2, home)
                        result2 = future.result()
                
                        if result2[0] :
                            print("info received")
                            addr = result2[1]
                            print(str(local_port))
                            subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out( home + '/.config/voider/self/' ), "-p", "UDP", "--dport", str(local_port), "-j", "REDIRECT", "--to-port", "1194"])
                            subprocess.run(["conntrack", "-D", "-p", "UDP"])
                            print("nat REDIRECT rule set")
                            time.sleep(25)
                
                            count = 0
                            connected = True
                            while connected :
                                if mymodule.ping2('172.31.0.' + str(idx)) :
                                    print("ping succeeded")
                                    count = 0
                                    time.sleep(15)
                                else :
                                    if count == 5 :
                                        connected = False
                                        subprocess.run(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out( home + '/.config/voider/self/' ), "-p", "UDP", "--dport", str(local_port), "-j", "REDIRECT", "--to-port", "1194"])
                                    else :
                                        print('ping ' + str(count) + ' failed')
                                        time.sleep(5)
                                        count = count + 1

def connect_to_clients(home):

    localpath = home + '/.config/voider/self/'
    with open(localpath + 'creds') as file:
        self = file.read().splitlines()[5][1:]
    file.close()

    with open(localpath + 'occupants') as file:
        clients = file.read().splitlines()
    file.close()

    idx = 1
    for client in clients :
        idx = idx + 1
        if client[0] == '1':
            cred = client[2:]
            with open(localpath + 'client_creds/' + cred + '/' + cred) as file:
                access = file.read().splitlines()
            file.close()

            temp = localpath + 'client_creds/' + cred
            
            threading.Thread(target=udp_punch, args=(access, self, cred, temp, idx, home, )).start()

with open("/etc/openvpn/home_voider") as file:
    home = file.read().splitlines()[0]
file.close()

with open(home + '/.config/voider/self/phone_number') as file:
    phone = file.read().splitlines()
file.close()

# place the needed nat rules 

subprocess.run(["iptables", "-t", "nat", "--flush"])


subprocess.run(["ip", "addr", "add", phone[1] + '/30', "dev", mymodule.getint_in( home + '/.config/voider/self/' )])

subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out( home + '/.config/voider/self/' ), "-j", "MASQUERADE"])


# into the tunnel :
subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", phone[0], "-j", "SNAT", "--to-source", "172.29.1.1"])
# out of the tunnel :
subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "all", "-j", "DNAT", "--to-destination", phone[0]])

localpath = home + '/.config/voider/self/'

with open(localpath + 'occupants') as file:
    clients = file.read().splitlines()
file.close()

m1 = []
m2 = []

x=1

for client in clients :
    if client[0] == '1':
        callee1 = '10.1.'+ str(x + 1) +'.1'
        callee2 = '172.29.'+ str(x + 1) + '.1'
    # into the tunnel :
        subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in( home + '/.config/voider/self/' ), "-d", callee1, "-p", "all", "-j", "DNAT", "--to-destination", callee2])
    # out of the tunnel :
        subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_in( home + '/.config/voider/self/' ), "-s", callee2, "-p", "all", "-j", "SNAT", "--to-source", callee1])
        m1.append(callee1)
        m2.append(callee2)
    x += 1

threading.Thread(target=mymodule.patch_caller, args=(home, m1, m2, )).start()

threading.Thread(target=connect_to_clients, args=(home, )).start()

os.chdir(localpath)

with open("creds") as file:
    L = file.read().splitlines()
    host = L[0][1:]
    username = L[3][1:]
    password = L[4][1:]
    server = L[5][1:]
file.close()

localpath = home + '/.config/voider/self/DoA'
remotepath = '/DoA'
while(True):
    print("uploading")
    mymodule.Upload(username, password, localpath, remotepath, host)
            
    time.sleep(60)


import urllib.request
import os
import paramiko
import time
import socket
import mymodule
import subprocess
import threading
from pathlib import Path

ended = False

def udp_punch(vps_ip, vps_port, local_port, server):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', local_port))
    addr = (vps_ip, vps_port)
    localpath = home + '/.config/voider/self/'
    with open("creds") as file:
        L = file.read().splitlines()
    file.close()
    
    self = L[5]
    message = b'\'' + self + ' ' + server

    threading.Thread(target=mymodule.send, args=(sock, addr, message)).start()

    data, addr = sock.recvfrom(1024)
    print('server received from vps : {} {}'.format(addr, data))
    temp = msg_to_addr_and_pair(data)
    addr = (temp[0], temp[1])
    pair = [temp[2], temp[3]]

    print(pair[0] + ' ' + pair[1])

    if pair[0] == server and pair[1] == self:
        ended = True
        sock.sendto(message, addr)

        data, addr = sock.recvfrom(1024)
        print('punch received: {} {}'.format(addr, data))

        sock.sendto(message, addr)

        data, addr = sock.recvfrom(1024)
        print('punch received: {} {}'.format(addr, data))

        sock.close()

        time.sleep(1)
    
    return addr
    

def worker(num):
    home = str(Path.home())
    localpath = home + '/.config/voider/certs/' + str(num) + '/'
    os.chdir(localpath)
    for cert in os.listdir('.') : 
        if os.path.isfile(cert) :
            #print(cert)
            with open(cert) as file:
                Lines = file.read().splitlines()
                name = cert
                print(Lines)
                subnetID = Lines[0][1]
                vps_ip = Lines[1][1:]
                username = Lines[2][1:]
                password = Lines[3][1:]
                server = Lines[5][1:]
                vps_port = Lines[6][1:]
    first = True
    local_port = 6868 + num
    while True :
        if  mymodule.isAlive(vps_ip, username, password, server, localpath):
            addr = udp_punch(vps_ip, vps_port, local_port, server)
            if not first :
                subprocess.run(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out( localpath ), "-s", addr[0], "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
            print("go")
            localpath = home + '/.config/voider/self/'
            subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out( localpath ), "-s", addr[0], "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
            localpath = home + '/.config/voider/certs/' + str(num) + '/'
            os.chdir(localpath)
            proc = subprocess.Popen(["ip", "netns", "exec", 'netns' + str(num),"openvpn", "--lport", local_port, "--remote", addr[0], addr[1], "--config", name])
            time.sleep(20)
            count = 0
            connected = True
            reconnect = True
            while connected :
                print('Worker' + str(num))
                if mymodule.ping("172.31.0.1", num) :
                    print("ping succeeded")
                    count = 0
                    time.sleep(15)
                    if first :
                        first = False
                        #into the network namespace :
                        subprocess.run(["ip", "route", "add", '10.' + str(num) + '.1.1', "via", '172.30.' + str(num) + '.2'])
                    if reconnect :
                        reconnect = False
                        #into the tunnel :
                        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "PREROUTING", "-i", 'veth' + str(num), "-d", '10.' + str(num) + '.1.1', "-p", "all", "-j", "DNAT", "--to-destination", "172.29.1.1"])
                        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.16.1.5", "-j", "SNAT", "--to-source", '172.29.' + subnetID + '.1'])
                        #out of the tunnel :
                        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", '172.29.' + subnetID + '.1', "-p", "all", "-j", "DNAT", "--to-destination", "172.16.1.5"])
                        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-s", "172.29.1.1", "-j", "SNAT", "--to-source", '10.' + str(num) + '.1.1'])
                else :
                    if count == 3 :
                        proc.terminate()
                        connected = False
                    print("ping failed")
                    time.sleep(5)
                    count = count + 1
    return


home = str(Path.home())

subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out( home + '/.config/voider/self' ), "-j", "MASQUERADE"])


os.chdir(home + '/.config/voider/certs')

with open("occupants") as file:
    Lines = file.read().splitlines()
        
print(Lines) 



netns = 2
for line in Lines :
    if line[0] == '1' :
        print(line)
        subprocess.run(["ip", "netns", "add", 'netns' + str(netns)])
        subprocess.run(["brctl", "addbr", 'br' + str(netns)])
        subprocess.run(["ip", "addr", 'add', '172.30.' + str(netns) + '.1/24', "dev", 'br' + str(netns)])
        subprocess.run(["ip", "link", "set", "dev", 'br' + str(netns), "up"])
        subprocess.run(["ip", "link", "add", 'veth' + str(netns), "type", "veth", "peer", "name", 'veth-br'  + str(netns)])
        subprocess.run(["ip", "link", "set", 'veth' + str(netns), "netns", 'netns' + str(netns)])
        subprocess.run(["brctl", "addif", 'br' + str(netns), 'veth-br'  + str(netns)])
        subprocess.run(["ip", "link", "set", "dev", 'veth-br'  + str(netns), "up"])
        netns = netns + 1

print("line")

netns = 2
for line in Lines :
    if line[0] == '1' :
        print(line)
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "addr", "add", '172.30.' + str(netns) + '.2/24', "dev", 'veth' + str(netns)])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "link", "set", "dev", "lo", "up"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "link", "set", "dev", 'veth' + str(netns), "up"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "route", "add", "default", "via", '172.30.' + str(netns) + '.1', "dev", 'veth' + str(netns)])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "iptables", "-A", "OUTPUT", "-o", 'veth' + str(netns), "-d", "172.31.0.1", "-j", "DROP"])
        netns = netns + 1


# spawn n processes, one for each ovpn client

netns = 2
for line in Lines :
    if line[0] == '1' :
        t = threading.Thread(target=worker, args=(netns,))
        netns = netns + 1
        t.start()

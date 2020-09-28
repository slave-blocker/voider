import urllib.request
import os
import time
import socket
import mymodule
import subprocess
import threading
import concurrent.futures
from pathlib import Path
import util



def udp_punch(vps_ip, vps_port, server, num):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 0))
    sock.settimeout(120)
    local_port = sock.getsockname()[1]
    address = (vps_ip, int(vps_port))
    
    with open(home + '/.config/voider/self/creds') as file:
        L = file.read().splitlines()
    file.close()
    
    self = L[5][1:]
    
    e = threading.Event()
    e.clear()
    print('punchit!' + str(local_port))
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.submit(mymodule.send, sock, address, self, server, e)
        future = executor.submit(mymodule.receive_client, sock, self, server, e, num)
        result = future.result()
        result.append(local_port)
        print("final")
    return result



def worker(num):
    home = str(Path.home())
    global phone
    localpath = home + '/.config/voider/certs/' + str(num)
    os.chdir(localpath)
    for cert in os.listdir('.') : 
        if os.path.isfile(cert) :
            #print(cert)
            with open(cert) as file:
                Lines = file.read().splitlines()
                name = cert
                subnetID = Lines[0][1]
                vps_ip = Lines[1][1:]
                username = Lines[2][1:]
                password = Lines[3][1:]
                server = Lines[4][1:]
                vps_port = Lines[5][1:]
    first = True
    #into the network namespace :
    subprocess.run(["ip", "route", "add", '10.' + str(num) + '.1.1', "via", '172.30.' + str(num) + '.2'])
    #into the tunnel :
    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "PREROUTING", "-i", 'veth' + str(num), "-d", '10.' + str(num) + '.1.1', "-p", "all", "-j", "DNAT", "--to-destination", "172.29.1.1"])
    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", phone[0], "-j", "SNAT", "--to-source", '172.29.' + subnetID + '.1'])
    #out of the tunnel :
    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", '172.29.' + subnetID + '.1', "-p", "all", "-j", "DNAT", "--to-destination", phone[0]])
    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-s", "172.29.1.1", "-j", "SNAT", "--to-source", '10.' + str(num) + '.1.1'])
    first = True
    while True :
        if  mymodule.isAlive(vps_ip, username, password, server, localpath):
            print("isAlive!")
            result = udp_punch(vps_ip, vps_port, server, num)
            print(str(result[0]))
            if result[0] :
                print("info received")
                addr = result[1]
                local_port = result[2]
                localdir = home + '/.config/voider/self/'
                if not first :
                    subprocess.run(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out( localdir ), "-s", temp, "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
                    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-D", "POSTROUTING", "-o", 'veth' + str(num), "-d", temp, "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out( localdir ))])
                temp = addr[0]
                here = home + '/.config/voider/certs/' + str(num) + '/'
                os.chdir(here)
                proc = subprocess.Popen(["ip", "netns", "exec", 'netns' + str(num), "openvpn", "--lport", str(local_port), "--remote", str(addr[0]), str(addr[1]), "--config", name, "--float"])
                time.sleep(20)
                
                count = 0
                connected = True
                while connected :
                    print('Worker' + str(num))
                    if mymodule.ping("172.31.0.1", num) :
                        print("ping succeeded")
                        count = 0
                        time.sleep(15)
                    else :
                        if count == 5 :
                            proc.terminate()
                            connected = False
                        else :
                            print('ping ' + str(count) + ' failed')
                            time.sleep(5)
                            count = count + 1
    return


home = str(Path.home())

#subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out( home + '/.config/voider/self' ), "-j", "MASQUERADE"])

subprocess.run(["iptables", "-t", "nat", "--flush"])
subprocess.run(["iptables", "-t", "filter", "--flush"])
subprocess.run(["killall", "openvpn"])



with open(home + '/.config/voider/self/phone_number') as file:
    phone = file.read().splitlines()
file.close()


os.chdir(home + '/.config/voider/certs')

with open("occupants") as file:
    Lines = file.read().splitlines()
file.close()

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
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns),"iptables", "-t", "nat", "--flush"])
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

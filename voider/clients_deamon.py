import urllib.request
import os
import paramiko
import time
import socket
import mymodule
import subprocess
import threading
from pathlib import Path
"""
def connect(ip, cert, localpath, netns):
    os.chdir(localpath)
    subprocess.run(["ip", "netns", "exec", 'netns' + str(netns),"openvpn", "--remote", ip, "1194", "--config", cert, "&"], shell=True)
    return
"""
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
                domain = Lines[1][1:]
                username = Lines[2][1:]
                password = Lines[3][1:]
    
    first = True
    while True :
        localpath = home + '/.config/voider/certs/' + str(num) + '/ext_ip/'
        mymodule.Download(username, password, localpath + 'ext_ip', domain)
        os.chdir(localpath)
        with open("ext_ip") as file:
            ip1 = file.read()
        print("go")
        localpath = home + '/.config/voider/self/'
        subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out( localpath ), "-s", ip1, "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
        localpath = home + '/.config/voider/certs/' + str(num) + '/'
        os.chdir(localpath)
        proc = subprocess.Popen(["ip", "netns", "exec", 'netns' + str(num),"openvpn", "--remote", ip1, "1194", "--config", name])
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
                    #into the netspace :
                    subprocess.run(["ip", "route", "add", '10.' + str(num) + '.1.1', "via", '172.30.' + str(num) + '.2'])
                if reconnect :
                    reconnect = False
                    #into the tunnel :
                    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "PREROUTING", "-i", 'veth' + str(num), "-d", '10.' + str(num) + '.1.1', "-p", "all", "-j", "DNAT", "--to-destination", "172.17.1.1"])
                    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.16.1.1", "-j", "SNAT", "--to-source", '172.17.' + subnetID + '.1'])
                    #out of the tunnel :
                    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", '172.17.' + subnetID + '.1', "-p", "all", "-j", "DNAT", "--to-destination", "172.16.1.1"])
                    subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-s", "172.17.1.1", "-j", "SNAT", "--to-source", '10.' + str(num) + '.1.1'])
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

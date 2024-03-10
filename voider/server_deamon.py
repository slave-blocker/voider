import urllib.request
import os
import time
import socket
import subprocess
import mymodule
import re
from pathlib import Path
import threading
import concurrent.futures



home = mymodule.get_home()

# place the needed nat rules 
subprocess.run(["iptables", "-t", "nat", "--flush"])
subprocess.run(["ip", "addr", "add", "172.16.19.86" + '/30', "dev", mymodule.getint_in()])

subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out(), "-j", "MASQUERADE"])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "brsip", "-s", "172.16.19.85", "-j", "SNAT", "--to-source", "172.18.0.2"])


# into the tunnel :
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.16.19.85", "-p", "udp", "!", "--dport", "5060", "-j", "SNAT", "--to-source", "172.29.1.1"])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.18.0.2", "-p", "udp", "--dport", "5060", "-j", "SNAT", "--to-source", "172.29.1.1"])


# out of the tunnel :
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "udp", "!", "--dport", "5060", "-j", "DNAT", "--to-destination", "172.16.19.85"])
subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.29.1.1", "-p", "udp", "--dport", "5060", "-j", "DNAT", "--to-destination", "172.18.0.2"])


localpath = home + '/.config/voider/self'

with open(localpath + '/occupants') as file:
    clients = file.read().splitlines()
file.close()

x=1

for client in clients :
    splitted_string = client.split("#")    
    if splitted_string[0][0] == '1' :    
        callee1 = '10.1.'+ str(x + 1) +'.1'
        callee2 = '172.29.'+ str(x + 1) + '.1'
    # nat into the bridge to fool conntrack :
    # 7000 + client idx 
        portroute = 7000 + (x + 1)
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-I", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "--dport", "5060", "-s", "172.16.19.85", "-d", '10.1.' + str(x + 1) + '.1', "-j", "DNAT", "--to", '172.19.0.2:' + str(portroute)])
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "--dport", "5060", "-s", "172.16.19.85", "-d", mymodule.replace_src_to_rtp((x + 1), False), "-j", "DNAT", "--to", '172.19.0.2:' + str(portroute), "-m", "comment", "--comment", "Normal sip"])
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "!", "--dport", "5060", "-s", "172.16.19.85", "-d", mymodule.replace_src_to_rtp((x + 1), False), "-j", "DNAT", "--to", str(callee2), "-m", "comment", "--comment", "rtp"])
        subprocess.run(["ip", "netns", "exec", "replay", "ip", "route", "add", '172.29.' + str(x + 1) + '.1', "via", "172.18.0.1"])
        subprocess.run(["ip", "netns", "exec", "replay", "iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", "vethsip", "-d", "172.19.0.2", "-p", "udp", "--dport", str(portroute), "-j", "DNAT", "--to-destination", '172.29.' + str(x + 1) + '.1:5060'])
    x += 1


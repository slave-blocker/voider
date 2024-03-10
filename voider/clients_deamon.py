import urllib.request
import os
import time
import socket
import mymodule
import subprocess
import threading
import concurrent.futures
from pathlib import Path
#import util_unused

def worker(num):
    home = mymodule.get_home()
    print("client n° " + str(threading.get_native_id()))
    localpath = home + '/.config/voider/servers/' + str(num) 
    
    L = mymodule.getfilename(localpath + '/ovpn')
    if L[0] :    
        cert = L[2]        

        self = cert[:-5]
        full_name = L[1]        
        #print(full_name)
        with open(full_name) as file:
            Lines = file.read().splitlines()
            file.close()  
              
        subnetID = Lines[0][1:]                
        #isSenator = Lines[1][1]        
        
        print(subnetID + ' ' + str(num))                
        #into the network namespace :
        subprocess.run(["ip", "route", "add", '10.' + str(num) + '.1.1', "via", '172.30.' + str(num) + '.2'])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-p", "udp", "-s", "172.29.1.1", "-j", "SNAT", "--to-source", '10.' + str(num) + '.1.1'])
        #into the tunnel :
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", 'veth' + str(num), "-p", "udp", "-d", '10.' + str(num) + '.1.1', "-j", "DNAT", "--to-destination", "172.29.1.1"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-p", "udp", "!", "--dport", "5060", "-s", "172.16.19.85", "-d", "172.29.1.1", "-j", "SNAT", "--to-source", '172.29.' + subnetID + '.1'])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-p", "udp", "--dport", "5060", "-s", "172.18.0.2", "-d", "172.29.1.1", "-j", "SNAT", "--to-source", '172.29.' + subnetID + '.1'])
        #out of the tunnel :
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-I", "PREROUTING", "-i", "tun0", "-d", '172.29.' + subnetID + '.1', "-p", "udp", "!", "--dport", "5060", "-j", "DNAT", "--to-destination", "172.16.19.85"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-I", "PREROUTING", "-i", "tun0", "-d", '172.29.' + subnetID + '.1', "-p", "udp", "--dport", "5060", "-j", "DNAT", "--to-destination", "172.18.0.2"])
        #nat into the bridge to fool conntrack :
        subprocess.run(["ip", "netns", "exec", "replay", "ip", "route", "add", '10.' + str(num) + '.1.1', "via", "172.18.0.1"])
        # 6000 + server idx
        portroute = 6000 + num
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "--dport", "5060", "-s", "172.16.19.85", "-d", '10.' + str(num) + '.1.1', "-j", "DNAT", "--to", '172.19.0.2:' + str(portroute), "-m", "comment", "--comment", "Normal sip"])
        subprocess.run(["ip", "netns", "exec", "replay", "iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", 'vethsip', "-d", "172.19.0.2", "-p", "udp", "--dport", str(portroute), "-j", "DNAT", "--to-destination", '10.' + str(num) + '.1.1:5060', "-m", "comment", "--comment", "Normal sip"])
        
        #GXP PATCH only incoming calls from the same subnet are recognized;
        #Ack gets routed just like rtp:
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "--dport", "5060", "-s", "172.16.19.85", "-d", mymodule.replace_src_to_rtp(num, True), "-j", "DNAT", "--to", '172.19.0.2:' + str(portroute), "-m", "comment", "--comment", "Normal sip"])
        #rtp:
        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in(), "-p", "udp", "!", "--dport", "5060", "-s", "172.16.19.85", "-d", mymodule.replace_src_to_rtp(num, True), "-j", "DNAT", "--to", '10.'+ str(num) +'.1.1', "-m", "comment", "--comment", "rtp" ])



        localoip_ssh_server = localpath + '/oip_ssh'

     
        L2 = [False, None]
        while True :
            while not L2[0] :            
                L2 = mymodule.getIP(localoip_ssh_server)
                if not L2[0] :
                    time.sleep(60)
                else :
                    addr = L2[1]                   
                    print('got ip address of server, over sftp over tor. -> ' + str(addr))
                
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', 0))
            local_port = sock.getsockname()[1]                        
# route incoming packets from that addr to the respective netns :                                    
            subprocess.run(["iptables", "-w", "2", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_out(), "-s", addr, "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
# this needs to be there because once the packets get into the default netns,
# they will not get masquaraded out for some unknown reason :                
            subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr, "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out())])
# start the tunnel :           
            proc = subprocess.Popen(["ip", "netns", "exec", 'netns' + str(num), "openvpn", "--lport", str(local_port), "--remote", str(addr), "--rport", "1194", "--config", full_name])
            time.sleep(1)
# flush conntrack entries both in the default namespace as in the respective netns :
            subprocess.run(["conntrack", "-D", "-p", "UDP", "-s", addr])
            subprocess.run(["conntrack", "-D", "-p", "UDP", "-d", addr])
            subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP", "-s", addr])
            subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP", "-d", addr])
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
                        L2 = [False, None]                        
# the dinamic ip might have changed therefore the iptable rules need to be deleted :
                        subprocess.run(["iptables", "-w", "2", "-t", "nat", "-D", "PREROUTING", "-i", mymodule.getint_out(), "-s", addr, "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
                        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-w", "2", "-t", "nat", "-D", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr, "-j", "SNAT", "--to-source", mymodule.get_ip_address(mymodule.getint_out())])
                    else :
                        print('ping ' + str(count) + ' failed')
                        time.sleep(5)
                        count = count + 1        
    else :
        print("no openvpn certificate present")    
    
    return

home = mymodule.get_home()


subprocess.run(["iptables", "-w", "2", "-t", "nat", "--flush"])
subprocess.run(["iptables", "-w", "2", "-t", "filter", "--flush"])

os.chdir(home + '/.config/voider/servers')

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
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns),"iptables", "-w", "2", "-t", "nat", "--flush"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns),"iptables", "-w", "2", "-t", "filter", "--flush"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "addr", "add", '172.30.' + str(netns) + '.2/24', "dev", 'veth' + str(netns)])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "link", "set", "dev", "lo", "up"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "link", "set", "dev", 'veth' + str(netns), "up"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ip", "route", "add", "default", "via", '172.30.' + str(netns) + '.1', "dev", 'veth' + str(netns)])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "iptables", "-w", "2", "-A", "OUTPUT", "-o", 'veth' + str(netns), "-d", "172.31.0.1", "-j", "DROP"])
        netns = netns + 1



# spawn n processes, one for each ovpn client

print("main " + str(os.getpid()))

with open(home + '/.config/voider/client_pid', 'w') as file:
    file.write(str(os.getpid()))
file.close()

N=[]
T=[]

netns = 2
for line in Lines :
    if line[0] == '1' :
        t = threading.Thread(target=worker, args=(netns, ))
        t.daemon = True
        N.append(netns)
        T.append(t)
    netns = netns + 1

time.sleep(10)

while True :
    c=0
    for thread in T :
        if not thread.is_alive() :
            T[c] = threading.Thread(target=worker, args=(N[c], ))            
            T[c].daemon = True
            T[c].start()
        else :
            print('thread ' + str(c) + ' is_alive')
            print(str(thread.is_alive()))
            print("indeed")
        c+=1
    time.sleep(30)

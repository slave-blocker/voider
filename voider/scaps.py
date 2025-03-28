import sys 
import os 
import subprocess
from scapy.all import *
from scapy.layers.inet import IP


#if the call comes from a server, network namespace (10.i.1.1). :
#readable_payload=readable_payload.replace("172.16.19.85", newsrc)
#the line 172.16.19.84 needs to be replaced with 172.16.XX.XX .
#in other words the amount of chars in the ip address being replaced needs to stay the same.

def from_server(src):

    c = int(src.split('.')[1])
    with open('/ram-dir/mapping_servers', 'r') as file:
        for index, line in enumerate(file):
            if index == (c-1):
                return str(line.strip())

def from_client(src):
                    
    c = int(src.split('.')[2])
    
    with open('/ram-dir/mapping_clients', 'r') as file:
        for index, line in enumerate(file):
            if index == (c-1):
                return str(line.strip())

def replace_src_to_rtp(src):
    if src.split('.')[0][1] == '0':
        return from_server(src)
    else:
        return from_client(src)



def chgSend(pckt):
    if IP in pckt:
        if UDP in pckt:
            #print("test test  " + str(pckt[IP].src))
            if pckt[IP].src != '172.18.0.2':
                if pckt[IP].src != '0.0.0.0':
                    ###GXP patch, only same lan : 172...
                    #print(pckt[IP].src)
                    #print(pckt[IP].src.split('.')[0])
                    newsrc = replace_src_to_rtp(pckt[IP].src)
                    
                    #if pckt[IP].src.split('.')[0][1] == '0':
                    #    newsrc = '172.27.' + str(pckt[IP].src.split('.')[1]) + '.1'
                    #else:
                    #    newsrc = str(pckt[IP].src)
                    
                    readable_payload = pckt[UDP].payload.load.decode('UTF8','replace')
                    #print(newsrc + "test test  111" + readable_payload)
                    readable_payload=readable_payload.replace("172.16.19.85", newsrc)
                    #print("test test  222" + readable_payload)
                    pckt[UDP].payload.load = bytes(readable_payload.encode('UTF8'))
                    pckt[UDP].sport=5060
                    wrpcap('go', pckt)
                    subprocess.call(["tcprewrite", "--infile=go", "--outfile=go2f", "--enet-smac=§1", "--enet-dmac=§2", '--srcipmap=' + pckt[IP].src + ':' + newsrc, "--dstipmap=172.18.0.2:172.16.19.85", "--fixcsum"])
                    pckt2 = rdpcap('go2f')
                    sendp(pckt2, iface="§3")
while 1:
    sniff(iface="breplay", prn=chgSend)

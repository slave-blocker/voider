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
                    #for 10.2-255.1.1 :
                    #172.16.10.12 -> 10.2.1.1
                    #172.16.10.13 -> 10.3.1.1
                    #172.16.10.14 -> 10.4.1.1
                    #172.16.10.19 -> 10.9.1.1
                    #172.16.11.10 -> 10.10.1.1
                    #172.16.11.19 -> 10.19.1.1
                    #172.16.12.10 -> 10.20.1.1
                    #172.16.19.19 -> 10.99.1.1
                    #172.16.20.10 -> 10.100.1.1
                    #172.16.29.19 -> 10.199.1.1
                    #172.16.30.10 -> 10.200.1.1
                    #172.16.30.11 -> 10.201.1.1
                    #172.16.35.15 -> 10.255.1.1
                                       #210 <- indexes  
    c = int(src.split('.')[1])
    
    z=True
    if c >= 200 and z:
        starter = 3
        #c0 = src.split('.')[1][2]
        c1 = src.split('.')[1][1]
        c2 = src.split('.')[1][0]
        z=False
    if c >= 100 and z:
        starter = 2
        #c0 = src.split('.')[1][2]
        c1 = src.split('.')[1][1]
        c2 = src.split('.')[1][0]
        z=False
    if c >= 10 and z:
        starter = 1
        #0xx
        #c0 = 0
        c1 = src.split('.')[1][1]
        c2 = src.split('.')[1][0]
        z=False
    if z :
        starter = 1
        #0xx
        #c0 = 0
        c1 = 0
        c2 = src.split('.')[1][0]

    return str('172.16.' + str(starter) + str(c1) + '.1' + str(c2))

def from_client(src):
                    #for 172.29.2-255.1 :
                           #starter
                    #172.16.40.12 -> 172.29.2.1
                    #172.16.40.13 -> 172.29.3.1
                    #172.16.40.14 -> 172.29.4.1
                    #172.16.40.19 -> 172.29.9.1
                    #172.16.41.10 -> 172.29.10.1
                    #172.16.41.11 -> 172.29.11.1
                    #172.16.42.10 -> 172.29.20.1
                    #172.16.49.19 -> 172.29.99.1
                    #172.16.50.10 -> 172.29.100.1
                    #172.16.59.19 -> 172.29.199.1
                    #172.16.60.10 -> 172.29.200.1
                    #172.16.60.11 -> 172.29.201.1
                    #172.16.65.15 -> 172.29.255.1
                              #marker
    c = int(src.split('.')[2])
    
    z=True
    if c >= 200 and z:
        starter = 6
        #c0 = src.split('.')[1][2]
        c1 = src.split('.')[1][1]
        c2 = src.split('.')[1][0]
        z=False
    if c >= 100 and z:
        starter = 5
        #c0 = src.split('.')[1][2]
        c1 = src.split('.')[1][1]
        c2 = src.split('.')[1][0]
        z=False
    if c >= 10 and z:
        starter = 4
        #0xx
        #c0 = 0
        c1 = src.split('.')[1][1]
        c2 = src.split('.')[1][0]
        z=False
    if z :
        starter = 4
        #0xx
        #c0 = 0
        c1 = 0
        c2 = src.split('.')[1][0]

    return str('172.16.' + str(starter) + str(c1) + '.1' + str(c2))


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

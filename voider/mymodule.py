import socket
import os
import subprocess
import re
import time
import random
from pathlib import Path
import fcntl
import struct
import select
import threading
import sys
import ipaddress


def from_server(c):
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
    num = int(c)
    z=True
    if num >= 200 and z:
        starter = 3
        #c0 = src.split('.')[1][2]
        c1 = c[1]
        c2 = c[0]
        z=False
    if num >= 100 and z:
        starter = 2
        #c0 = src.split('.')[1][2]
        c1 = c[1]
        c2 = c[0]
        z=False
    if num >= 10 and z:
        starter = 1
        #0xx
        #c0 = 0
        c1 = c[1]
        c2 = c[0]
        z=False
    if z :
        starter = 1
        #0xx
        #c0 = 0
        c1 = 0
        c2 = c[0]

    return str('172.16.' + str(starter) + str(c1) + '.1' + str(c2))

def from_client(c):
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
    num = int(c)
    z=True
    if num >= 200 and z:
        starter = 6
        #c0 = src.split('.')[1][2]
        c1 = c[1]
        c2 = c[0]
        z=False
    if num >= 100 and z:
        starter = 5
        #c0 = src.split('.')[1][2]
        c1 = c[1]
        c2 = c[0]
        z=False
    if num >= 10 and z:
        starter = 4
        #0xx
        #c0 = 0
        c1 = c[1]
        c2 = c[0]
        z=False
    if z :
        starter = 4
        #0xx
        #c0 = 0
        c1 = 0
        c2 = c[0]
    return str('172.16.' + str(starter) + str(c1) + '.1' + str(c2))


def replace_src_to_rtp(c, from_serverQ):
    if from_serverQ:
        return from_server(str(c))
    else:
        return from_client(str(c))



def get_home():
    with open("/etc/openvpn/home_voider") as file:
        home = file.read().splitlines()[0]
        file.close()
    return home

def replace_Element(L, index, el):
    temp=[]
    i = 0
    for element in L :
        if( index == i ):
            temp.append(el)
        else :
            temp.append(L[i])
        i+=1
    return temp

def getint_in():
    home = get_home()    
    localpath = home + '/.config/voider/self/' 
    with open(localpath + 'int_in') as file:
        int_eth = file.read()
    file.close()
    return int_eth

def getint_out():
    home = get_home()    
    localpath = home + '/.config/voider/self/' 
    with open(localpath + 'int_out') as file:
        int_wlan = file.read()
    file.close()
    return int_wlan

def getname(occupants, index):
    with open(occupants) as file:
        Lines = file.readlines()
        name = Lines[index - 2].split('#')[1].strip();
    file.close()
    return name

def get_phone():
    home = get_home()    
    with open(home + '/.config/voider/self/phone_number') as file:
        phone = file.read().splitlines()[0]
    file.close()
    return phone

# gets the name of the first file inside the directory
# in this context, directories of interest only have one file.
def getfilename(path):
    for name in os.listdir(path) :
        #print(path + '/' + cert) 
        if os.path.isfile(path + '/' + name) :
            full_name = path + '/' + name
            return [True, full_name, name]       
    return [False, None, None]

def findfirst(occupants):
    with open(occupants) as file:
        Lines = file.readlines() 
# Strips the newline character 
    file.close()
    count = 1
    for line in Lines:
        if(line.strip()[0] == '0'):
            return count 
        count = count + 1
    return count

def modify(occupants, index, do, name = None):
    with open(occupants) as file:
        Lines = file.readlines() 
    file.close()
    print(Lines)
    if len(Lines) == 0 :
        Lines.append('1#' + name)
    else :
        if ( index - 2 ) <= (len(Lines) - 1)  : 
            if ( index - 2 ) == (len(Lines) - 1) :
                if do :
                    Lines[index - 2] = str(1) + '#' + name
                if not do :
                    Lines[index - 2] = str(0)
            else :
                if do :
                    Lines[index - 2] = str(1) + '#' + name + '\n'
    
                if not do :
                    Lines[index - 2] = str(0) + '\n'
        else :
            Lines.append('\n1#' + name )
        
    with open(occupants, 'w') as file:
        file.writelines(Lines)
    file.close()
    return
    
def appendRoute(route = None):
    home = get_home()    
    with open(home + '/.config/voider/self/occupants') as file:
        Lines = file.readlines() 
    file.close()
    List = []
    j = 2
    for line in Lines :
        if line[0] == '1' :
            List.append('\nroute 172.29.' + str(j) + '.1' + ' 255.255.255.255 172.31.0.' + str(j))
        j = j + 1
    
    with open('/etc/openvpn/backup') as file:
        Lines = file.readlines()
    file.close()
    for routes in List :
        Lines.append(routes)
    if route != None : 
        Lines.append(route)
    
    Times = []
    for line in Lines :
        z = False
        z2 = False

        if "dhcp-option" in line :
            z = True
        if "block-outside-dns" in line :
            z = True
        if "redirect-gateway" in line :
            z = True
        if "server 10." in line :
            z2 = True
        
        if z :
            Times.append('#' + line)
        else :
            if z2 :#TODO can this network be shorter?
                Times.append("server 172.31.0.0 255.255.255.0\n")
            else :
                Times.append(line)
    
    
    with open('/etc/openvpn/server.conf', 'w') as file:
        file.writelines(Times)
    file.close()
    return

def changeCert(Lines):
   
    Times = []
    for line in Lines :
        z = False

        if "nobind" in line :
            z = True
       
        if z :
            Times.append('#' + line)
        else :
            Times.append(line)
    return Times

def Download_onions_IP(localoip_ssh, onion):
    if os.path.exists(localoip_ssh + "/self") :    
        home = get_home()    
        sftp = home + '/.config/voider/sftp'
        #print("1 " + sftp)
        key = localoip_ssh + "/self"
        localoip = localoip_ssh + "/oip"
        #print("2 " + key)
        #print("4 " + onion)
        #print("6 " + localoip)
        cwd = localoip_ssh + '/../tor'       
        proc = subprocess.Popen([sftp, key, "self", onion, "/oip", localoip, "tor", "get", cwd])
        print("after subprocess.Popen @Download_onions_IP")        
        try :
            proc.wait(30)
        except subprocess.TimeoutExpired:
            print("Download_onions_IP sftp TimeoutExpired")
            proc.terminate()
            return False
        except Exception:
            print("Download_onions_IP sftp failed")
            proc.terminate()
            return False
        return True
    else :
        print("no certificate present")
        sys.exit()

def isIPv4_addr(ip_addr) :
    try:
        ip = ipaddress.ip_address(ip_addr)
        return True    
    except Exception :
        return False

def getIP(localoip_ssh) :
    isDead = True
    oip = 0

    with open(localoip_ssh + '/hostname') as file:
        onion = file.read().splitlines()[0]
        file.close()

    localoip = localoip_ssh + '/oip'    
    fail = 0
    while isDead:
        
        if Download_onions_IP(localoip_ssh, onion) :
            print("after Download_onions_IP")
            with open(localoip) as file:
                DoA = file.read().splitlines()
                file.close()
            try :
                print("after try")
                print("0 this is AoD : " + DoA[0])
                if isIPv4_addr(DoA[0]) :#if no ip was downloaded, within 10 secs, the file just contains a 0.
                    print("Ip is valid : " + DoA[0])
                    isDead = False
                    oip = DoA[0]
                else:
                    print("Ip is invalid : " + DoA[0])
                    time.sleep(60)
            except Exception :
                print("error @ Download_onions_IP ")
                time.sleep(60)
        else:
            if fail == 3 :                
                return [False, None]                    
            else :                
                fail += 1
    return [True, oip] 
    

def ping(host, netns):
    try:
        subprocess.run(["ip", "netns", "exec", 'netns' + str(netns), "ping", "-c", "1", "-W", "3", host], check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False
        
def ping2(host):
    try:
        subprocess.run(["ping", "-c", "1", "-W", "3", host], check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', (ifname[:15].encode('utf-8')))
    )[20:24])

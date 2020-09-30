import paramiko
import socket
import os
import subprocess
import re
import time
import util
import random
from pathlib import Path
import fcntl
import struct
import select

def patch(home, m1, m2):
    pattern = re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')
    active = False
    on = False
    off = False
    proc = subprocess.Popen(["tcpdump", "-i", getint_in( home + '/.config/voider/self' ), "-l"], stdout=subprocess.PIPE)
    for row in iter(proc.stdout.readline, b''):
        temp = row.rstrip()
        if "INVITE" in str(temp) and not on:
            print(' A gotcha : ' + str(temp))   # process here
        
            # extracting the IP addresses 
            ip1 = pattern.findall(str(temp))[0]
            ip2 = pattern.findall(str(temp))[1]
            print('gotcha 2: ' + ip1 + '   ' + ip2)
            if ip1[1] == '0' or ip2[1] == '0' :
                if ip1[1] == '0' :
                    if ip1[3] == '1':
                        idx = m1.index(ip1)
                        ip1 = m2[idx]
                    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", getint_in( home + '/.config/voider/self' ), "-j", "DNAT", "--to-destination", ip1])
                    on = True
                if ip2[1] == '0' :
                    if ip2[3] == '1':
                        idx = m1.index(ip2)
                        ip2 = m2[idx]
                    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", getint_in( home + '/.config/voider/self' ), "-j", "DNAT", "--to-destination", ip2])
                    on = True
        if "BYE" in str(temp) or "Terminated" in str(temp) or "Busy" in str(temp):
            print(' B gotcha : ' + str(temp))   # process here
            on = False 
            # extracting the IP addresses 
            ip1 = pattern.findall(str(temp))[0]
            ip2 = pattern.findall(str(temp))[1]
            print('gotcha 2: ' + ip1 + '   ' + ip2)
            if ip1[1] == '0' or ip2[1] == '0' :
                if ip1[1] == '0' :
                    if ip1[3] == '1':
                        idx = m1.index(ip1)
                        ip1 = m2[idx]
                    subprocess.run(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", getint_in( home + '/.config/voider/self' ), "-j", "DNAT", "--to-destination", ip1])
                    off = True
                if ip2[1] == '0' :
                    if ip2[3] == '1':
                        idx = m1.index(ip2)
                        ip2 = m2[idx]
                    subprocess.run(["iptables", "-t", "nat", "-D", "PREROUTING", "-i", getint_in( home + '/.config/voider/self' ), "-j", "DNAT", "--to-destination", ip2])
                    off = True
    
def getint_in( localpath ):
    os.chdir(localpath)
    with open("int_in") as file:
        int_eth = file.read()
    file.close()
    return int_eth

def getint_out( localpath ):
    os.chdir(localpath)
    with open("int_out") as file:
        int_wlan = file.read()
    file.close()
    return int_wlan

def getname( occupants, index ):
    with open(occupants) as file:
        Lines = file.readlines()
        name = Lines[index - 2].split('#')[1].strip();
    file.close()
    return name

def findfirst( occupants ):
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
    
def modify( occupants, index, do, name = None):
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
            Lines.append('\n1#' + name)
        
    with open(occupants, 'w') as file:
        file.writelines(Lines)
    file.close()
    return
    
def appendRoute( home, route = None):
    with open(home + '/.config/voider/self/occupants') as file:
        Lines = file.readlines() 
    file.close()
    List = []
    j = 2
    for line in Lines :
        if line[0] == '1' :
            List.append('\nroute 172.29.1.' + str(j) + ' 255.255.255.255')
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
        if "server 10.8" in line :
            z2 = True
        
        if z :
            Times.append('#' + line)
        else :
            if z2 :
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
    return Lines
    
def addClient(name):
   
    localpath = home + '/.config/voider/self/'

    os.chdir(localpath)

    with open("creds") as file:
        L = file.read().splitlines()
        host = L[0][1:]
        username = L[3][1:]
        password = L[4][1:]
        server = L[5][1:]
    file.close()
    
    with open("clients") as file:
        L = file.readlines()
    file.close()
    
    L.append(name + '\n')
    
    with open("clients", "w") as file:
        file.writelines(L)
    file.close()
    
    localpath = home + '/.config/voider/self/clients'
    remotepath = '/var/sftp/' + server + '/clients'
    
    Upload(username, password, localpath, remotepath, host)
    
def delClient(Lines):
   
    localpath = home + '/.config/voider/self/'

    os.chdir(localpath)
    
    with open("clients") as file:
        Lines = file.readlines()
    file.close()
    
    Times = []
    for line in Lines :
        if not name in line :
            Times.append(line)
    
    with open("clients", "w") as file:
        file.writelines(Times)
    file.close()
    
    with open("creds") as file:
        L = file.read().splitlines()
        host = L[0][1:]
        username = L[3][1:]
        password = L[4][1:]
        server = L[5][1:]
    file.close()
    
    localpath = home + '/.config/voider/self/clients'
    remotepath = '/var/sftp/' + server + '/clients'
    
    Upload(username, password, localpath, remotepath, host)

def Upload(username, password, localpath, remotepath, host):
    # Open a transport
    transport = paramiko.Transport((host, 22))

    # Auth    
    transport.connect(None, username, password)

    # Go!    
    sftp = paramiko.SFTPClient.from_transport(transport)
        
    # Upload
    sftp.put(localpath, remotepath)

    # Close
    if sftp: sftp.close()
    if transport: transport.close()
    
    return
    
def Download(username, password, localpath, remotepath, host):
    # Open a transport
    transport = paramiko.Transport((host, 22))

    # Auth    
    transport.connect(None, username, password)

    # Go!    
    sftp = paramiko.SFTPClient.from_transport(transport)
        
    # Download
    sftp.get(remotepath, localpath)

    # Close
    if sftp: sftp.close()
    if transport: transport.close()
    
    return
# paramiko.util.log_to_file("paramiko.log")

def isAlive(vps_ip, username, password, peer, localpath):
    isDead = True
    localpath = localpath + '/DoA/DoA'
    remotepath = '/' + peer + '/DoA'
    while isDead:
        Download(username, password, localpath, remotepath, vps_ip)
        with open(localpath) as file:
            DoA = file.read().splitlines()
        file.close()
        if DoA[0] == '1':
            isDead = False
        else:
            time.sleep(60)
    return True

def send(sock, addr, self, peer, event, limit, sleep):
    message = self + ' ' + peer
    message = str.encode(message)
    count = 0
    while count < limit and not event.is_set():
        print('gogogo ' + str(count) + self + ' ' + peer)
        sock.sendto(message, addr)
        time.sleep(random.randint(1, sleep))
        count = count + 1
        
def receive_meeting_port(sock, event):
    home = str(Path.home())
    localdir = home + '/.config/voider/self/'
    try:
        data, addr = sock.recvfrom(1024)
        event.set()
    except socket.timeout:
        print("exceeded timeout, for info from vps")
        event.set()
        time.sleep(5)
        result = [False, None]
        return result
        
    print('peer received from vps : {} {}'.format(addr, data))
    addr = util.msg_to_addr(data)
    
    #sock.close()
    result = [True, addr]
        
    return result


def receive_server(sock, self, peer, event):
    home = str(Path.home())
    try:
        data, addr = sock.recvfrom(1024)
    except socket.timeout:
        print("exceeded timeout, for info from vps")
        event.set()
        time.sleep(10)
        result = [False, None]
        return result
    
    print('peer received from vps : {} {}'.format(addr, data))
    temp = util.msg_to_addr_and_pair(data)
    addr = (temp[0], temp[1])
    pair = [temp[2], temp[3]]

#    print(pair[0] + ' ' + pair[1])
#    print("punch")
#    print(peer + ' ' + self)


    if pair[0] == peer and pair[1] == self:
        event.set()
        print("punch the hole through !")
        message = self + ' ' + peer
        message = str.encode(message)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        print("punch done, now rest...")

        print("activate the client's nat rule .")
        time.sleep(10)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        print("just sent 6 packets")        
        
        sock.close()
    
        result = [True, addr]
        
        return result
    else:
        result = [False, addr]
        
        return result    
    
def receive_client(sock, self, peer, event, num):
    home = str(Path.home())
    localdir = home + '/.config/voider/self/'
    try:
        data, addr = sock.recvfrom(1024)
    except socket.timeout:
        print("exceeded timeout, for info from vps")
        event.set()
        time.sleep(10)
        result = [False, None]
        return result
        
    print('peer received from vps : {} {}'.format(addr, data))
    temp = util.msg_to_addr_and_pair(data)
    addr = (temp[0], temp[1])
    pair = [temp[2], temp[3]]

    #print(pair[0] + ' ' + pair[1])
    #print("punch")
    #print(peer + ' ' + self)


    if pair[0] == peer and pair[1] == self:
        event.set()
        print("punch the hole through !")
        message = self + ' ' + peer
        message = str.encode(message)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        sock.sendto(message, addr)
        print("punch done, now rest...")
        time.sleep(5)
        
        subprocess.run(["conntrack", "-D", "-p", "UDP"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP"])
        subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", getint_out( localdir ), "-s", addr[0], "-j", "DNAT", "--to", '172.30.' + str(num) + '.2'])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "iptables", "-t", "nat", "-A", "POSTROUTING", "-o", 'veth' + str(num), "-d", addr[0], "-j", "SNAT", "--to-source", get_ip_address(getint_out( localdir ))])
        subprocess.run(["conntrack", "-D", "-p", "UDP"])
        subprocess.run(["ip", "netns", "exec", 'netns' + str(num), "conntrack", "-D", "-p", "UDP"])

        print("expecting incoming packets to activate own nat rule.")
        time.sleep(10)
        
        sock.close()
    
        result = [True, addr]
        
        return result
    else:
        result = [False, addr]
        
        return result    

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

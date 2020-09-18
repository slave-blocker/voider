import paramiko
import socket
import os
import subprocess
import re


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
    
    with open('/etc/openvpn/server.conf', 'w') as file:
        file.writelines(Lines)
    file.close()
    return

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
    while isDead:
        localpath = localpath + '/DoA/DoA'
        remotepath = '/' + peer + '/DoA'
        Download(username, password, localpath, remotepath, vps_ip):
        with open(localpath) as file:
            DoA = file.read()
        file.close()
        if DoA == '1':
            isDead = False
        else:
            time.sleep(60)
    return True
            
def send(sock, addr, message):
    count = 0
    global ended
    while count < 24 and not ended:
        sock.sendto(message, addr)
        time.sleep(5)
        count = count + 1


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
        
        
        

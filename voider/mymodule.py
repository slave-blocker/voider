import paramiko
import socket
import os
import subprocess



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
            List.append('\nroute 172.17.1.' + str(j) + ' 255.255.255.255')
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

def Upload(username, password, localpath, host):
    # Open a transport
    transport = paramiko.Transport((host, 22))

    # Auth    
    transport.connect(None, username, password)

    # Go!    
    sftp = paramiko.SFTPClient.from_transport(transport)
        
    # Upload
    sftp.put(localpath, "/ext_ip")

    # Close
    if sftp: sftp.close()
    if transport: transport.close()
    
    return
    
def Download(username, password, localpath, host):
    # Open a transport
    transport = paramiko.Transport((host, 22))

    # Auth    
    transport.connect(None, username, password)

    # Go!    
    sftp = paramiko.SFTPClient.from_transport(transport)
        
    # Upload
    sftp.get( "/ext_ip", localpath)

    # Close
    if sftp: sftp.close()
    if transport: transport.close()
    
    return
# paramiko.util.log_to_file("paramiko.log")

def ping(host):
    try:
        subprocess.run(["ping", "-c", "1", "-W", "3", host], check=True)
        return True
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return False

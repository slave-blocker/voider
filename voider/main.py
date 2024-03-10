import urllib.request
import os
import sys
import re
import time
import mymodule
import socket
import subprocess
from pathlib import Path
import shutil
from shutil import copyfile

home = str(Path.home())

print("welcome")

if not os.path.exists(home + '/.config/voider/self/int_in') :
    print("Incoming interface not defined, the one connected to the phone .")
    subprocess.run(["ls", "/sys/class/net"])
    choice = input("Please type one from the above list :")
    file  = open(home + '/.config/voider/self/int_in', "w+")
    file.write(choice)
    file.close()

if not os.path.exists(home + '/.config/voider/self/int_out') :
    print("Outgoing interface not defined, the one directed to the internet .")
    subprocess.run(["ls", "/sys/class/net"])
    choice = input("Please type one from the above list :")
    file  = open(home + '/.config/voider/self/int_out', "w+")
    file.write(choice)
    file.close()


if not os.path.exists("/etc/openvpn/backup") :
    file  = open("/etc/openvpn/backup", "w+")
    copyfile("/etc/openvpn/server.conf", "/etc/openvpn/backup")
    file.close()



print("choose option :")

print("to quit - just press enter.")
print("1 - create a client connection to another server")
print("2 - delete a client connection to another server")
print("3 - call pivpn, to add a client connection to this server")
print("4 - call pivpn, to revoke a client connection to this server")
SenaTor = True

print(" after most executed options, a reboot is done .")

choice = input("Enter choice integer : ")

if choice == '1' :
    print('place client_certs.zip inside ' + home + '/.config/voider/servers/new_server/')
    os.chdir(home + '/.config/voider/servers/')
    index = mymodule.findfirst("occupants")
    os.chdir(home + '/.config/voider/servers/new_server/')    
    input("Press enter when done")    
    
    subprocess.run(["unzip", "client_certs.zip"])
    subprocess.run(["rm", "client_certs.zip"])       
    
    ovpn_cert = mymodule.getfilename(home + '/.config/voider/servers/new_server/ovpn')
    if not ovpn_cert[0]:       
        print("certificates not given (ovpn)")    
        sys.exit()

    if not os.path.exists(home + '/.config/voider/servers/new_server/oip_ssh') :
        print("certificates not given (oip_ssh)")    
        sys.exit()

    if not os.path.exists(home + '/.config/voider/servers/new_server/tor') :
        print("server pubkey not given (fingerprint, 4 sftp mitm check)")    
        sys.exit()
    
    if os.path.exists(home + '/.config/voider/servers/' + str(index + 1)) :
        subprocess.run(["rm", "-r", "-f", home + '/.config/voider/servers/' + str(index + 1)])
    
    mymodule.modify(home + '/.config/voider/servers/occupants', (index + 1), True, ovpn_cert[2])
#client_certs :
#/ovpn/ovpn_cert
#/oip_ssh/hostname (onion)
#/oip_ssh/self (ssh key, to be used only by sftp)
#/tor/host.pub (system ed25519 key)
#/tor/KnownHost (temp var to be used by the client)

    shutil.copytree(os.getcwd(), home + '/.config/voider/servers/' + str(index + 1))
    os.chdir(home + '/.config/voider/servers/' + str(index + 1))    
    subprocess.run(["chmod", "-R", "600", "."])

    # the folder "oip_ssh", contains the ssh key for the senator.
    # the retrieval of the ip address is with -> self@address.onion .                        

    subprocess.run(["rm", "-r", "-f", home + '/.config/voider/servers/new_server/'])
    os.mkdir(home + '/.config/voider/servers/new_server/')

    #subprocess.run(["reboot"]) 
            

if choice == '2' :
    print("please type the index \n")
    print("i.e. x in 10.x.1.1 \n ( x >= 2 )")
    
    os.chdir(home + '/.config/voider/servers/')
    index = input("Enter index integer : ")
    if os.path.exists(home + '/.config/voider/servers/' + str(index)) :
        mymodule.modify( "occupants", int(index), False )    
        subprocess.run(["rm", "-r", "-f", home + '/.config/voider/servers/' + index + '/'])
        #subprocess.run(["reboot"])


if choice == '3' :
    if not os.path.exists(home + "/.config/voider/self/new_client") :
        os.mkdir( home + "/.config/voider/self/new_client", 0o755 )                            

    name = input("Enter a Name for the Client:")
    if os.path.exists('/etc/openvpn/ccd/' + name) :
        print("Client name exists")
        sys.exit()

    subprocess.run(["pivpn", "add", "-n", name, "nopass"])

    os.chdir(home + '/.config/voider/self/')
    index = mymodule.findfirst("occupants")
    List = ['ifconfig-push 172.31.0.' + str(index + 1) + ' 255.255.255.0\n',
    "push \"route 172.29.1.1 255.255.255.255 172.31.0.1\"\n",
    'iroute 172.29.' + str(index + 1) + '.1' + ' 255.255.255.255']
    os.chdir('/etc/openvpn/ccd/')
    #the server has a file for every ovpn client with its name in '/etc/openvpn/ccd/'
    #this is used to push routes on the client, aswell as to setup iroutes.
    with open(name, 'w') as file:
        file.writelines(List)
        file.close()
    
    route = '\nroute 172.29.' + str(index + 1) + '.1 255.255.255.255 172.31.0.' + str(index + 1)
    mymodule.appendRoute(route)
    os.chdir(home + '/.config/voider/self/')
    mymodule.modify("occupants", (index + 1), True, name)
    

    os.chdir(home + '/ovpns/')
    with open(name + '.ovpn') as file:
        List2 = file.readlines()
        file.close()
    List3 = mymodule.changeCert(List2)

    List1 = ['#' + str(index + 1) + '\n']
    
    List1.append("#1\n")
    
    with open(name + '.ovpn', '+w') as file:
        file.writelines(List1)
        file.writelines(List3)
    file.close()

    # put the openvpn certificate :
    os.mkdir(home + "/.config/voider/self/new_client/ovpn", 0o755 )    
    copyfile(home + '/ovpns/' + name + '.ovpn', home + '/.config/voider/self/new_client/ovpn/' + name + '.ovpn')    

#/oip_ssh/hostname (onion)
#/oip_ssh/self (ssh key, to be used only by sftp)
    
    shutil.copytree(home + '/.config/voider/self/oip_ssh/', home + '/.config/voider/self/new_client/oip_ssh/')        
    # provide the host public key, of this machine, such that the client can verify the fingerprint.    
    # such that a man-in-the-middle attack can be avoided .   
    os.mkdir(home + '/.config/voider/self/new_client/tor', 0o755 )        
    copyfile('/etc/ssh/ssh_host_ed25519_key.pub', home + '/.config/voider/self/new_client/tor/host.pub')
    subprocess.run(["touch", home + '/.config/voider/self/new_client/tor/KnownHost' ])
        

    os.chdir(home + "/.config/voider/self/new_client")
    # this is given through a secured channel to the client :
    subprocess.run(["zip", "-m", "-r", "client_certs.zip", "."])
    #subprocess.run(["reboot"])

if choice == '4' :
    print("please type the index \n")
    print("i.e. x in 10.1.x.1 \n ( x >= 2 )")
    
    os.chdir(home + '/.config/voider/self/')
    index = input("Enter index integer : ")
    name = mymodule.getname( "occupants", int(index) )
    print(name)
    mymodule.modify("occupants", int(index), False ) 
    mymodule.appendRoute()
    subprocess.run(["pivpn", "revoke", "-y", name])
    #subprocess.run(["reboot"])


import urllib.request
import os
import paramiko
import time
import mymodule
import socket
import subprocess
import sqlite3
from pathlib import Path
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
    
if not os.path.exists(home + '/.config/voider/self/creds') :
    print("Sftp server not defined.")
    sftp = []
    choice = input("Please type the ip of the vps :")
    sftp.append('#' + choice + '\n')
    choice = input("Please type the read only user for the vps :")
    sftp.append('#' + choice + '\n')
    choice = input("Please type the read only password for the vps :")
    sftp.append('#' + choice )
    choice = input("Please type the read write user for the vps :")
    sftp.append('#' + choice + '\n')
    choice = input("Please type the read write password for the vps :")
    sftp.append('#' + choice )
    choice = input("Please type the folder's name in the vps :")
    sftp.append('#' + choice )
    choice = input("Please type the port number that the vps is listening on:")
    sftp.append('#' + choice )
    file  = open(home + '/.config/voider/self/creds', "w+")
    file.writelines(sftp)
    file.close()
    del sftp[4:5]
    file  = open(home + '/.config/voider/self/access_creds', "w+")
    file.writelines(sftp)
    file.close()




print("choose option :")

print("to quit - just press enter.")
print("1 - create a client connection to anouther server")
print("2 - delete a client connection to anouther server")
print("3 - call pivpn, to add a client connection to this server")
print("4 - call pivpn, to revoke a client connection to this server")
print("5 - Import access credentials file, from a client")
print("6 - Create access credentials file, for a server.")


print(" after each executed option a reboot is done .")

choice = input("Enter choice integer : ")

if choice == '1' :
    print('place cert inside' + home + '/.config/voider/certs/New/')
    os.chdir(home + '/.config/voider/certs/')
    index = mymodule.findfirst("occupants")
    os.chdir(home + '/.config/voider/certs/new/')
    input("Press enter when done")
    
    for cert in os.listdir('.') : 
        if os.path.isfile(cert) :
            print(cert) 

    os.chdir(home + '/.config/voider/certs/')
    done = False
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            print(name)
            if(name == str(index + 1)):
                os.rename(home + '/.config/voider/certs/new/' + cert, home + '/.config/voider/certs/' + str(index + 1) + '/' + cert )
                done = True
                print('yo' + str(index + 1)) 
                mymodule.modify( "occupants", (index + 1), True, cert)
    if done == False :
        os.mkdir( home + '/.config/voider/certs/' + str(index + 1), 0o755 )
        os.mkdir( home + '/.config/voider/certs/' + str(index + 1) + '/DoA', 0o755 )
        os.rename(home + '/.config/voider/certs/new/' + cert, home + '/.config/voider/certs/' + str(index + 1) + '/' + cert )
        mymodule.modify( "occupants", (index + 1), True, cert)
    subprocess.run(["reboot"])

if choice == '2' :
    print("please type the index \n")
    print("i.e. x in 10.x.1.1 \n ( x >= 2 )")
    
    os.chdir(home + '/.config/voider/certs/')
    index = input("Enter index integer : ")
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            print(name)
            if(name == index):
                mymodule.modify( "occupants", int(index), False )    
                os.chdir(home + '/.config/voider/certs/' + index + '/')
                for cert in os.listdir('.') : 
                    if os.path.isfile(cert) :
                        print(cert)
                        os.remove(cert)
    subprocess.run(["reboot"])


if choice == '3' :
    name = input("Enter a Name for the Client:")
    with open(home + '/.config/voider/self/creds') as file :
        List1 = file.readlines()
    file.close()
    del List1[4:5]
    List1.append('\n')
    #print(List1)
    subprocess.run(["pivpn", "add", "-n", name, "nopass"])
    os.chdir(home + '/.config/voider/self/')
    index = mymodule.findfirst("occupants")
    List = ['ifconfig-push 172.31.0.' + str(index + 1) + ' 255.255.255.0\n',
    "push \"route 172.29.1.1 255.255.255.255 172.31.0.1\"\n",
    'iroute 172.29.' + str(index + 1) + '.1' + ' 255.255.255.255']
    os.chdir('/etc/openvpn/ccd/')
    with open(name, 'w') as file:
        file.writelines(List)
    file.close()
    os.chdir('/etc/openvpn/')
    if not os.path.exists("/etc/openvpn/backup") :
        file  = open("/etc/openvpn/backup", "w+")
        copyfile("/etc/openvpn/server.conf", "/etc/openvpn/backup")
        file.close()
    route = '\nroute 172.29.' + str(index + 1) + '.1 255.255.255.255 172.31.0.' + str(index + 1)
    mymodule.appendRoute( home, route)
    os.chdir(home + '/.config/voider/self/')
    mymodule.modify("occupants", (index + 1), True, name)
    os.chdir(home + '/ovpns/')
    with open(name + '.ovpn') as file:
        List2 = file.readlines()
    file.close()
    List1.insert(0, '#' + str(index + 1) + '\n')
    with open(name + '.ovpn', '+w') as file:
        file.writelines(List1)
        file.writelines(List2)
    file.close()
    subprocess.run(["reboot"])

if choice == '4' :
    print("please type the index \n")
    print("i.e. x in 10.1.x.1 \n ( x >= 2 )")
    
    os.chdir(home + '/.config/voider/self/')
    index = input("Enter index integer : ")
    name = mymodule.getname( "occupants", int(index) )
    mymodule.modify( "occupants", int(index), False ) 
    mymodule.appendRoute( home)
    subprocess.run(["pivpn", "revoke", "-y", name])
    subprocess.run(["reboot"])

if choice == '5' :
    print('Place access credentials inside :' + home + '/.config/voider/self/New/')
    print("The name of the file of the access credentials must be the same as the name\n")
    print("of the certificate given to the client. Without the '\"'.ovpn'\"' extension.")

    input("Press enter when done")
    os.chdir(home + '/.config/voider/self/New/')

    for creds in os.listdir('.') : 
        if os.path.isfile(creds) :
            print(creds)
    
    with open(home + '/.config/voider/self/occupants') as file :
        clients = file.read().splitlines()
    file.close()
    
    
    res = [i for i in clients if creds in i]
    if res:
        os.mkdir(home + '/.config/voider/self/client_creds/' + creds, 0o755 )
        os.mkdir(home + '/.config/voider/self/client_creds/' + creds + '/DoA', 0o755 )
        os.rename(home + '/.config/voider/self/New/' + creds, home + '/.config/voider/self/client_creds/' + creds + '/' + creds)
    else:
        print("Invalid access credentials. From unknown client.")

if choice == '6' :
    print("The access credentials file needs to have the same name")
    print("as the name of the certificate handed out by the server. ")
    print("Without the '\"'.ovpn'\"' extension. ")
    
    print("The following certificates are available :")
    
    with open(home + '/.config/voider/certs/occupants') as file :
        certs = file.read().splitlines()
    file.close()
    
    for cert in certs:
        if cert[0] == '1'
            print(cert[2:])
    choice = input("Enter certificate's name : ")

    res = [i for i in certs if choice in i]
    if res:
        copyfile(home + '/.config/voider/self/access_creds', home + '/.config/voider/self/handout/' + choice)
    else :
        print("Invalid access credentials. For unknown server.")
    

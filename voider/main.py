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
    file_obj  = open(home + '/.config/voider/self/int_in', "w+")
    file_obj.write(choice)
    file_obj.close()

if not os.path.exists(home + '/.config/voider/self/int_out') :
    print("Outgoing interface not defined, the one directed to the internet .")
    subprocess.run(["ls", "/sys/class/net"])
    choice = input("Please type one from the above list :")
    file_obj  = open(home + '/.config/voider/self/int_out', "w+")
    file_obj.write(choice)
    file_obj.close()
    
if not os.path.exists(home + '/.config/voider/self/creds') :
    print("Sftp server not defined.")
    sftp = []
    choice = input("Please type the domain of the sftp server :")
    sftp.append('#' + choice + '\n')
    choice = input("Please type the user for the sftp server :")
    sftp.append('#' + choice + '\n')
    choice = input("Please type the password for the sftp server :")
    sftp.append('#' + choice )
    file_obj  = open(home + '/.config/voider/self/creds', "w+")
    file_obj.writelines(sftp)
    file_obj.close()


print("choose option :")

print("to quit - just press enter.")
print("1 - create a client connection to anouther server")
print("2 - delete a client connection to anouther server")
print("3 - call pivpn, to add a client connection to this server")
print("4 - call pivpn, to revoke a client connection to this server")

print(" after each executed option a reboot is done .")

choice = input("Enter choice integer : ")

if choice == '1' :
    print('place cert inside' + home + '/.config/voider/certs/new/')
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
        os.mkdir( home + '/.config/voider/certs/' + str(index + 1) + '/ext_ip', 0o755 )
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
    with open(home + '/.config/voider/self/creds') as file_obj :
        List1 = file_obj.readlines()
    file_obj.close()
    List1.append('\n')
    #print(List1)
    subprocess.run(["pivpn", "add", "-n", name, "nopass"])
    os.chdir(home + '/.config/voider/self/')
    index = mymodule.findfirst("occupants")
    List = ['ifconfig-push 172.31.0.' + str(index + 1) + ' 255.255.255.0\n',
    "push \"route 172.17.1.1 255.255.255.255 172.31.0.1\"\n",
    'iroute 172.17.' + str(index + 1) + '.1' + ' 255.255.255.255']
    os.chdir('/etc/openvpn/ccd/')
    with open(name, 'w') as file:
        file.writelines(List)
    file.close()
    os.chdir('/etc/openvpn/')
    if not os.path.exists("/etc/openvpn/backup") :
        file_obj  = open("/etc/openvpn/backup", "w+")
        copyfile("/etc/openvpn/server.conf", "/etc/openvpn/backup")
        file_obj.close()
    route = '\nroute 172.17.' + str(index + 1) + '.1 255.255.255.255 172.31.0.' + str(index + 1)
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

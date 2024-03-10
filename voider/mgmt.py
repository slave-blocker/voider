import os
import utils_server
import pwd
from pathlib import Path
from shutil import copyfile
import sys

home = str(Path.home())

if not os.path.exists("/etc/openvpn/home_voider") :
    file  = open("/etc/openvpn/home_voider", "w+")
    file.write(home)
    file.close()


print("choose option :")

print("to quit - just press enter.")
print("1 - Setup self IP Address, to be accessed over sftp over tor .")
print("2 - Delete self IP Address, to be accessed over sftp over tor .")

if len(sys.argv) > 1 :
    choice=1
else :
    choice = input("Enter choice integer : ")

if choice == '1' :    
    name1 = "self"
    #pass1 = input("Enter password to read only : ")
    
    #folder = "self"

    z=False
    for p in pwd.getpwall():
        if(p[0] == name1):
            z=True
            print("User already exists")

    if not z :
        utils_server.addSftpUserToSelf()

if choice == '2' :
    utils_server.delSftpUserToSelf()

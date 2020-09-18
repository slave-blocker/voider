import os
import utils
import pwd
from shutil import copyfile


print("choose option :")

print("to quit - just press enter.")
print("1 - create a user ")
print("2 - delete a user ")

choice = input("Enter choice integer : ")

if choice == '1' :
    
    name1 = input("Enter username to read and write : ")
    pass1 = input("Enter password to read and write : ")

    name2 = input("Enter username to read only : ")
    pass2 = input("Enter password to read only : ")

    z=False
    for p in pwd.getpwall():
        if(p[0] == name1):
            z=True
            print("User already exists")

    if not z :
        utils.addSftpUser(name1, pass1, name2, pass2)
    

if choice == '2' :
    
    print("The following users exist :")
    L = []
    os.chdir('/etc/ssh/voider/')
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            print('\n' + name)
            L.append(name)
    name1 = input("Enter username to delete : ")
    
    if name1 in L:
        utils.delSftpUser(name1)
    else :
        print("Username does not exist.")

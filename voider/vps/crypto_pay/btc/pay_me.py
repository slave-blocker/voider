import os
import subprocess
import json
import time
import utils
import pwd
from shutil import copyfile


os.chdir("/root/crypto_pay/btc/")

with open("/root/newuser") as file:
    List = file.read().splitlines()
file.close()

newuser = List[0]
addr = List[1]

payed = False
count = 0 

while not payed and count < 0 :

    with open("/root/crypto_pay/btc/confirmed", "w+") as confirmed:
        subprocess.run(["./electrum-3.3.8-x86_64.AppImage", "getaddressbalance", addr ], stdout=confirmed)
    confirmed.close()

    with open("/root/crypto_pay/btc/confirmed") as confirmed:
        confirm = confirmed.read()
    confirmed.close()

    #print(confirm)

    # parse x:
    y = json.loads(confirm)

    #print(y["confirmed"])

    if int(y["confirmed"]) >= 100000 :
        payed = True
    else :
        time.sleep(60)

    count = count + 1

with open("/root/newuser") as file:
    List = file.readlines()
file.close()

del List[0]
del List[0]

with open("/root/crypto_pay/btc/pubkey.asc", "w+") as creds:
    creds.writelines(List)
creds.close()

subprocess.run(["gpg", "--import", "/root/crypto_pay/btc/pubkey.asc" ])

found = False
temp = newuser
count = -3
while not found:
    count = count + 3
    z=False
    for p in pwd.getpwall():
        if(p[0] == temp):
            z=True
            print("User already exists")
    if z :
        temp = newuser + '_' + str(count)
    else :
        found = True

user_rw = newuser + '_' + str(count)
user_r = newuser + '_' + str(count + 1)
folder = newuser + '_' + str(count + 2)

subprocess.run(["./pass.sh"])

with open("/root/crypto_pay/btc/pass.txt") as password1:
    pas1 = password1.read().splitlines()[0]
password1.close()

print("pass1 : " + pas1)

subprocess.run(["./pass.sh"])

with open("/root/crypto_pay/btc/pass.txt") as password2:
    pas2 = password2.read().splitlines()[0]
password2.close()

print("pass2 : " + pas2)

access = [user_rw + '\n', pas1 + '\n', user_r + '\n', pas2 + '\n', folder]

try :
    os.remove('/var/sftp/newuser/creds.gpg')
except Exception :
    print("creds.gpg not there")

with open("/root/crypto_pay/btc/creds", "w+") as creds:
    creds.writelines(access)
creds.close()

utils.addSftpUser(user_rw, pas1, user_r, pas2, folder)

subprocess.run(["gpg", "--recipient", newuser, "--encrypt", "--trust-model", "always", "/root/crypto_pay/btc/creds" ])

copyfile('/root/crypto_pay/btc/creds.gpg', '/var/sftp/newuser/creds.gpg' )

os.remove('/root/crypto_pay/btc/creds.gpg')

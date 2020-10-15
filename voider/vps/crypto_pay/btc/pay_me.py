import os
import subprocess
import json
import time
import utils
import pwd
from shutil import copyfile

os.rename("/root/pay_me.sh", "/root/crypto_pay/btc/pay_me.sh")

os.rename("/var/sftp/newuser/address", "/var/sftp/newuser/processing")
os.rename("/var/sftp/newuser/newuser", "/var/sftp/newuser/payment")

os.chdir("/root/crypto_pay/btc/")

with open("/root/newuser") as file:
    List = file.read().splitlines()
file.close()

newuser = List[0]
addr = List[1]

with open("/var/sftp/newuser/address") as file:
    current_addr = file.read().splitlines()[0]
file.close()

payed = False
count = 0 

if addr == current_addr:

    subprocess.run(["/root/crypto_pay/btc/electrum_daemon.sh"])

    # sleep a bit, be polite to the daemon ...

    time.sleep(3)

    while not payed and count < 18 :

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
            time.sleep(600)

        count = count + 1

#payed = True

if payed :

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

    os.rename("/root/crypto_pay/btc/creds.gpg", '/var/sftp/newuser/' + addr)

    subprocess.run(["/root/crypto_pay/btc/call_rm_creds.sh", '/var/sftp/newuser/' + addr])

    with open("/root/crypto_pay/btc/addresses") as addresses:
        L = addresses.read()
    addresses.close()

    aList = json.loads(L)

    del aList[0]
    
    #subprocess.run(["/root/crypto_pay/btc/", '/var/sftp/newuser/' + addr])

    # now kill the daemon, because it won't work otherwise

    subprocess.run(["/root/crypto_pay/btc/kill_daemon.sh"])

    time.sleep(3)

    with open("/root/crypto_pay/btc/newaddress", "w+") as newaddress:
        subprocess.run(["/root/crypto_pay/btc/electrum-3.3.8-x86_64.AppImage", "createnewaddress"], stdout=newaddress)
    newaddress.close() 

    with open("/root/crypto_pay/btc/newaddress") as newaddress:
        newaddr = newaddress.read().splitlines()[0]
    newaddress.close()

    aList.append(newaddr)

    L = json.dumps(aList)

    with open("/root/crypto_pay/btc/addresses", "w+") as addresses:
        addresses.write(L)
    addresses.close()

    with open("/var/sftp/newuser/address", "w+") as address:
        address.write(aList[0])
    address.close()

os.rename("/root/crypto_pay/btc/pay_me.sh", "/root/pay_me.sh")
os.rename("/var/sftp/newuser/processing", "/var/sftp/newuser/address")
os.rename("/var/sftp/newuser/payment", "/var/sftp/newuser/newuser")

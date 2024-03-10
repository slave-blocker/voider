import os
import sys
import subprocess
from shutil import copyfile

def addSftpUserToSelf():

    with open("/etc/openvpn/home_voider") as file:
        home = file.read().split()[0]
        file.close()

    if not os.path.exists("/var/sftp") :
        subprocess.run(["mkdir", "/var/sftp/"])
        subprocess.run(["chown", "root:root", "/var/sftp"])
        subprocess.run(["chmod", "755", "/var/sftp"])
        os.mkdir("/etc/ssh/voider/", 0o755 )
        file  = open("/etc/ssh/voider/backup", "w+")
        copyfile("/etc/ssh/sshd_config", "/etc/ssh/voider/backup")
        file.close()
    
    try: 
        subprocess.run(["useradd", "--create-home", "self"])
    except: 
        print('Something went wrong  24')
    
    #setPassword(user_r, pass2)

    try: 
        subprocess.run(["mkdir", '/var/sftp/self'])
    except: 
        print('Something went wrong  31')

    try: 
        subprocess.run(["chown", 'root:root', '/var/sftp/self'])
    except: 
        print('Something went wrong  36')

    try: 
        subprocess.run(["chmod", "755", '/var/sftp/self'])
    except: 
        print('Something went wrong  41')
    
    try: 
        subprocess.run(["touch", '/var/sftp/self/oip'])
    except: 
        print('Something went wrong  46')

    try: 
        subprocess.run(["chown", 'self:self', '/var/sftp/self/oip'])
    except: 
        print('Something went wrong  51')

    try: 
        subprocess.run(["chmod", "400", '/var/sftp/self/oip'])
    except: 
        print('Something went wrong  56')
    
    try: 
        os.mkdir('/etc/ssh/voider/self', 0o755 )
    except: 
        print('Something went wrong  61')


    
    List2 = [
    '\n\n\nMatch User self',
    "\nForceCommand internal-sftp",
    "\nPasswordAuthentication no",
    '\nChrootDirectory /var/sftp/self',
    "\nPermitTunnel no",
    "\nAllowAgentForwarding no",
    "\nAllowTcpForwarding no",
    "\nX11Forwarding no"
    ]
    
    try: 
        with open('/etc/ssh/voider/self/conf', "w+") as file :
            file.writelines(List2)
        file.close()
    except: 
        print('Something went wrong  81')
    
    try: 
        with open("/etc/ssh/voider/backup") as file :
            back = file.readlines()
        file.close()
    except: 
        print('Something went wrong  88')
        

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    try: 
        with open("/etc/ssh/sshd_config", 'w') as file :
            file.writelines(back)
            file.writelines(List1)
        file.close()
    except: 
        print('Something went wrong  106')
        
    if not os.path.exists("/etc/tor/backup") :
        copyfile("/etc/tor/torrc", "/etc/tor/backup")

    with open("/etc/tor/backup") as file :
        back = file.readlines()
    file.close()
 
    List2 = [
    '\n\n\n',
    '\nHiddenServiceDir /var/lib/tor/sshd/',
    '\nHiddenServicePort 22 127.0.0.1:22'
    ]

    back.extend(List2)
    
    #with open("/etc/tor/torrc", 'w') as file :
    #    file.writelines(back)
    #file.close()

    subprocess.run(["service", "tor", "restart"])
    
    try: 
        with open("/etc/tor/torrc", 'w+') as file :
            file.writelines(back)
        file.close()
    except: 
        print('Something went wrong  134')


    # create the ssh key for the clients to connect over tor.
    try: 
        print("1111")
        os.mkdir(home + '/.config/voider/self/oip_ssh', 0o755)
        print("2222")
        os.chdir(home + '/.config/voider/self/oip_ssh')
        print("3333")        
    except: 
        print('Something went wrong  142')    

    try: 
        subprocess.run(["cp", "/var/lib/tor/sshd/hostname", "."])
    except: 
        print('Something went wrong  147')    

    
    try: 
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-b", "384", "-q", "-f", "self", "-N", ""])
    except: 
        print('Something went wrong  153')    

    try: 
        os.mkdir("/home/self/.ssh/", 0o755 )
    except: 
        print('Something went wrong  158')        

    try: 
        copyfile("self.pub", "/home/self/.ssh/authorized_keys")
    except: 
        print('Something went wrong  163')        

    try: 
        subprocess.run(["rm", "self.pub"])
    except: 
        print('Something went wrong  168')        
    
    try: 
        subprocess.run(["chmod", "640", "self"])
    except: 
        print('Something went wrong  173')        

    

    subprocess.run(["service", "ssh", "restart"])


def delSftpUserToSelf():        

    with open("/etc/openvpn/home_voider") as file:
        home = file.read().split()[0]
        file.close()
   
    # delete the ssh key for the clients to connect over tor.

    try: 
        os.remove('/var/sftp/self/oip')
    except: 
        print('Something went wrong  191')
    
    try: 
        os.rmdir('/var/sftp/self')
    except: 
        print('Something went wrong  197')
    
    try: 
        os.remove(home + '/.config/voider/self/oip_ssh/self')
    except: 
        print('Something went wrong  201')
    
    try: 
        os.remove(home + '/.config/voider/self/oip_ssh/hostname')
    except: 
        print('Something went wrong  206')
    
    try: 
        os.rmdir(home + '/.config/voider/self/oip_ssh')
    except: 
        print('Something went wrong  211')

    try: 
        subprocess.run(["userdel", "-r", "self"])
    except: 
        print('Something went wrong  216')
    
    try: 
        os.remove('/etc/ssh/voider/self/conf')
    except: 
        print('Something went wrong  221')
        
    try: 
        os.rmdir('/etc/ssh/voider/self')
    except: 
        print('Something went wrong  226')
    
    try: 
        with open("/etc/ssh/voider/backup") as file :
            back = file.readlines()
        file.close()
    except: 
        print('Something went wrong  233')
    
    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    try: 
        with open("/etc/ssh/sshd_config", 'w') as file :
            file.writelines(back)
            file.writelines(List1)
        file.close()
    except: 
        print('Something went wrong  250')


    try: 
        with open("/etc/tor/backup") as file :
            back = file.readlines()
        file.close()
    except: 
        print('Something went wrong  258')

    try: 
        with open("/etc/tor/torrc", 'w') as file :
            file.writelines(back)
        file.close()
    except: 
        print('Something went wrong  265')
 

    subprocess.run(["service", "tor", "restart"])
    subprocess.run(["service", "ssh", "restart"])


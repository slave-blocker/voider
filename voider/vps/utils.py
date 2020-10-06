import os
import subprocess
from shutil import copyfile


def setPassword(userName:str, password:str):
    p = subprocess.Popen([ "/usr/sbin/chpasswd" ], universal_newlines=True, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate(userName + ":" + password + "\n")
    #assert p.wait() == '0'
    #if stdout or stderr:
    #    raise Exception("Error encountered changing the password!")
    



def addSftpUser(user_rw, pass1, user_r, pass2, folder):

    if not os.path.exists("/var/sftp") :
        subprocess.run(["mkdir", "/var/sftp/"])
        subprocess.run(["chown", "root:root", "/var/sftp"])
        subprocess.run(["chmod", "755", "/var/sftp"])
        os.mkdir("/etc/ssh/voider/", 0o755 )
        file  = open("/etc/ssh/voider/backup", "w+")
        copyfile("/etc/ssh/sshd_config", "/etc/ssh/voider/backup")
        file.close()
    
    subprocess.run(["useradd", user_rw])
    setPassword(user_rw, pass1)
    subprocess.run(["useradd", user_r])
    setPassword(user_r, pass2)
    subprocess.run(["usermod", "-a", "-G", user_rw, user_r])
    subprocess.run(["mkdir", '/var/sftp/' + folder])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + folder])
    subprocess.run(["chmod", "750", '/var/sftp/' + folder])
    subprocess.run(["touch", '/var/sftp/' + folder + '/DoA'])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + folder + '/DoA'])
    subprocess.run(["chmod", "750", '/var/sftp/' + folder + '/DoA'])
    subprocess.run(["touch", '/var/sftp/' + folder + '/clients'])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + folder + '/clients'])
    subprocess.run(["chmod", "750", '/var/sftp/' + folder + '/clients'])

    with open('/var/sftp/' + folder + '/DoA', 'w') as file:
        file.write('0')
    file.close()
    
    with open('/root/servers') as file:
        servers = file.readlines()
    file.close()
    
    servers.append(folder + '\n')
    
    with open("/root/servers", "w") as file:
        file.writelines(servers)
    file.close()

    os.mkdir('/etc/ssh/voider/' + user_rw, 0o755 )
    
    List2 = [
    '\n\nMatch User ' + user_rw ,
    "\nForceCommand internal-sftp",
    "\nPasswordAuthentication yes",
    "\nChrootDirectory /var/sftp",
    "\nPermitTunnel no",
    "\nAllowAgentForwarding no",
    "\nAllowTcpForwarding no",
    "\nX11Forwarding no\n",
    '\nMatch User ' + user_r ,
    "\nForceCommand internal-sftp",
    "\nPasswordAuthentication yes",
    "\nChrootDirectory /var/sftp",
    "\nPermitTunnel no",
    "\nAllowAgentForwarding no",
    "\nAllowTcpForwarding no",
    "\nX11Forwarding no"
    ]
    
    with open('/etc/ssh/voider/' + user_rw + '/conf', "w+") as file :
        file.writelines(List2)
    file.close()
    
    List2 = [
    user_rw ,
    '\n' + user_r,
    '\n' + folder
    ]
    
    with open('/etc/ssh/voider/' + user_rw + '/names', "w+") as file :
        file.writelines(List2)
    file.close()
    
    with open("/etc/ssh/voider/backup") as file :
        back = file.readlines()
    file.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file :
        file.writelines(back)
        file.writelines(List1)
    file.close()
    
    subprocess.run(["service", "ssh", "restart"])

def delSftpUser(user_rw):
    
    with open('/etc/ssh/voider/' + user_rw + '/names') as file :
        L = file.read().splitlines()
    file.close()
    
    user_r = L[1]
    folder = L[2]
    
    with open("/root/servers") as file:
        Lines = file.readlines()
    file.close()
    
    Times = []
    for line in Lines :
        if not folder in line :
            Times.append(line)
    
    with open("/root/servers", "w") as file:
        file.writelines(Times)
    file.close()
    
    os.remove('/var/sftp/' + folder + '/DoA')
    os.remove('/var/sftp/' + folder + '/clients')
    os.rmdir('/var/sftp/' + folder )
    
    subprocess.run(["deluser", user_rw])
    subprocess.run(["deluser", user_r])
    
    os.remove('/etc/ssh/voider/' + user_rw + '/conf')
    os.remove('/etc/ssh/voider/' + user_rw + '/names')
    os.rmdir('/etc/ssh/voider/' + user_rw)
    
    with open("/etc/ssh/voider/backup") as file :
        back = file.readlines()
    file.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file :
                List = file.readlines()
            file.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file :
        file.writelines(back)
        file.writelines(List1)
    file.close()
    
    subprocess.run(["service", "ssh", "restart"])


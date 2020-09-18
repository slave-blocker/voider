import os
import subprocess


def setPassword(userName:str, password:str):
    p = subprocess.Popen([ "/usr/sbin/chpasswd" ], universal_newlines=True, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdout, stderr) = p.communicate(userName + ":" + password + "\n")
    assert p.wait() == '0'
    if stdout or stderr:
        raise Exception("Error encountered changing the password!")




def addSftpUser(user_rw, pass1, user_r, pass2):

    if not os.path.exists("/var/sftp") :
        subprocess.run(["mkdir", "/var/sftp/"])
        subprocess.run(["chown", "root:root", "/var/sftp"])
        subprocess.run(["chmod", "755", "/var/sftp"])
        os.mkdir("/etc/ssh/voider/", 0o755 )
        file_obj  = open("/etc/ssh/voider/backup", "w+")
        copyfile("/etc/ssh/sshd_config", "/etc/ssh/voider/backup")
        file_obj.close()
    
    subprocess.run(["useradd", user_rw])
    setPassword(user_rw, pass1)
    subprocess.run(["useradd", user_r])
    setPassword(user_r, pass2)
    subprocess.run(["usermod", "-a", "-G", user_rw, user_r])
    subprocess.run(["mkdir", '/var/sftp/' + user_rw])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + user_rw])
    subprocess.run(["chmod", "750", '/var/sftp/' + user_rw])
    subprocess.run(["touch", '/var/sftp/' + user_rw + '/DoA'])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + user_rw + '/DoA'])
    subprocess.run(["chmod", "750", '/var/sftp/' + user_rw + '/DoA'])
    subprocess.run(["touch", '/var/sftp/' + user_rw + '/clients'])
    subprocess.run(["chown", user_rw + ':' + user_rw, '/var/sftp/' + user_rw + '/clients'])
    subprocess.run(["chmod", "750", '/var/sftp/' + user_rw + '/clients'])

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
    
    with open('/etc/ssh/voider/' + user_rw + '/conf', "w+") as file_obj :
        file_obj.writelines(List2)
    file_obj.close()
    
    List2 = [
    user_rw ,
    '\n' + user_r
    ]
    
    with open('/etc/ssh/voider/' + user_rw + '/names', "w+") as file_obj :
        file_obj.writelines(List2)
    file_obj.close()
    
    with open("/etc/ssh/voider/backup") as file_obj :
        back = file_obj.readlines()
    file_obj.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file_obj :
                List = file_obj.readlines()
            file_obj.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file_obj :
        file_obj.writelines(back)
        file_obj.writelines(List1)
    file_obj.close()
    
    subprocess.run(["service", "ssh", "restart"])

def delSftpUser(user_rw):
        
    os.remove('/var/sftp/' + user_rw + '/DoA')
    os.remove('/var/sftp/' + user_rw + '/clients')
    os.rmdir('/var/sftp/' + user_rw )
    
    subprocess.run(["deluser", user_rw])
    
    with open('/etc/ssh/voider/' + user_rw + '/names') as file_obj :
        user_r = file_obj.readlines()[1]
    file_obj.close()
    
    subprocess.run(["deluser", user_r])
    
    os.remove('/etc/ssh/voider/' + user_rw + '/conf')
    os.remove('/etc/ssh/voider/' + user_rw + '/names')
    os.rmdir('/etc/ssh/voider/' + user_rw)
    
    with open("/etc/ssh/voider/backup") as file_obj :
        back = file_obj.readlines()
    file_obj.close()

    os.chdir('/etc/ssh/voider/')
    List1 = []
    for name in os.listdir('.') : 
        if os.path.isdir(name) :
            with open('/etc/ssh/voider/' + name + '/conf') as file_obj :
                List = file_obj.readlines()
            file_obj.close()
            List1.extend(List)

    with open("/etc/ssh/sshd_config", 'w') as file_obj :
        file_obj.writelines(back)
        file_obj.writelines(List1)
    file_obj.close()
    
    subprocess.run(["service", "ssh", "restart"])


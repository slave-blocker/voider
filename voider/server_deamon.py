import urllib.request
import os
import paramiko
import time
import socket
import subprocess
import mymodule
import re
from pathlib import Path

home = str(Path.home())

os.chdir("/etc/openvpn/ccd")

n = len([name for name in os.listdir('.') if os.path.isfile(name)])

print(n)

# place the needed nat rules 

subprocess.run(["iptables", "-t", "nat", "--flush"])

subprocess.run(["ip", "addr", "add", "172.16.1.2/30", "dev", mymodule.getint_in( home + '/.config/voider/self' )])

subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_out( home + '/.config/voider/self' ), "-j", "MASQUERADE"])


# into the tunnel :
subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", "tun0", "-s", "172.16.1.1", "-j", "SNAT", "--to-source", "172.17.1.1"])
# out of the tunnel :
subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", "tun0", "-d", "172.17.1.1", "-p", "all", "-j", "DNAT", "--to-destination", "172.16.1.1"])


for x in range(1, n+1):

    callee1 = '10.1.'+ str(x + 1) +'.1'
    callee2 = '172.17.'+ str(x + 1) + '.1'
# into the tunnel :
    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", mymodule.getint_in( home + '/.config/voider/self' ), "-d", callee1, "-p", "all", "-j", "DNAT", "--to-destination", callee2])
# out of the tunnel :
    subprocess.run(["iptables", "-t", "nat", "-A", "POSTROUTING", "-o", mymodule.getint_in( home + '/.config/voider/self' ), "-s", callee2, "-p", "all", "-j", "SNAT", "--to-source", callee1])

remotepath = "/self"
localpath = home + '/.config/voider/self/'

os.chdir(localpath)

with open("ext_ip") as file:
    ip1 = file.read()

print(ip1)
"""
while(1):

    ip2 = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    print(ip2)
    if socket.inet_pton(socket.AF_INET, ip1) != socket.inet_pton(socket.AF_INET, ip2):
        ip1 = ip2
    
        with open(localpath, 'w') as file:
            file.write(ip1)


        # Open a transport
        transport = paramiko.Transport((host,port))

        # Auth    
        transport.connect(None,username,password)

        # Go!    
        sftp = paramiko.SFTPClient.from_transport(transport)
        # Upload
        sftp.put(localpath, remotepath)

        # Close
        if sftp: sftp.close()
        if transport: transport.close()
    
    time.sleep(15)
"""

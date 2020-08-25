import urllib.request
import os
import paramiko
import time
import socket
import subprocess
import re

os.chdir("/etc/openvpn/ccd")

n = len([name for name in os.listdir('.') if os.path.isfile(name)])

print(n)

# place the needed nat rules 

subprocess.run(["iptables", "-t", "nat", "--flush"])

for x in range(1, n+1):
# into the tunnel :
    callee1 = '10.1.'+ str(x) +'.1'
    callee2 = '172.17.1.'+ str(x)
    subprocess.run(["iptables", "-t", "nat", "-A", "PREROUTING", "-i", "enp1s0", "-d", callee1, "-p", "all", "-j", "DNAT", "--to-destination", callee2])
#iptables -t nat -A PREROUTING -i eth0 -d 10.1.2.1 -p all -j DNAT --to-destination 172.17.1.2

#iptables -t nat -A POSTROUTING -o tun0 -s 172.16.1.1 -j SNAT --to-source 172.17.1.1

# out of the tunnel :

#iptables -t nat -A PREROUTING -i tun0 -d 172.17.1.1 -p all -j DNAT --to-destination 172.16.1.1

#iptables -t nat -A POSTROUTING -o eth0 -s 172.17.1.2 -j SNAT --to-source 10.1.2.1

with open(localpath) as file:
    ip1 = file.read()

print(ip1)

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

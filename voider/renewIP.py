import urllib.request
import os
import time
import socket
from requests import get
from pathlib import Path

if os.path.exists("/var/sftp/self/oip") :

    while True:
        with open("/var/sftp/self/oip") as file:
            ip1 = file.read()
            file.close()

        print("local " + ip1)        
        try:
            ip2 = str(get('https://api.ipify.org').text)
            print("url " + ip2)
            if ip1 != ip2 :
                ip1 = ip2
                with open("/var/sftp/self/oip", "w") as file:
                    file.write(ip1)
                    file.close()
        except Exception:
            print("exceeded timeout")
    
        time.sleep(60)

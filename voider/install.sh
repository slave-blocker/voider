#! /bin/bash

find . -name "blub" -type f -delete
cd ..
mv voider/ ~/.config/
sudo apt-get install tcpdump conntrack python3-paramiko bridge-utils
curl -L https://install.pivpn.io | bash


#! /bin/bash

# after running "install as root" execute these lines as you :

find . -name "blub" -type f -delete

sed -i 's/§/'"$(whoami)"'/g' rc.local

sudo mv rc.local /etc/

cd ..
mkdir ~/.config
mv voider ~/.config/voider

sudo apt-get install tcpdump tcpreplay conntrack bridge-utils zip openssh-server
curl -L https://install.pivpn.io | bash

sudo echo "/home/$(whoami)" > home_voider

sudo mv home_voider /etc/openvpn/
# after this just reboot
# then use sudo -E python3 main.py :) 

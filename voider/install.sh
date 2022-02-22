#! /bin/bash

find . -name "blub" -type f -delete

sed -i 's/§/'"$(whoami)"'/g' rc.local
sed -i 's/§/'"$(whoami)"'/g' caller.sh

sudo mv rc.local /etc/

cd ..
mv voider/ ~/.config/

sudo apt-get install tcpdump conntrack python3-paramiko bridge-utils
curl -L https://install.pivpn.io | bash


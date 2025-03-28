#!/bin/sh

find . -name "blub" -type f -delete

apk add iptables sed perl git bind-tools net-tools newt curl tcpdump bridge-utils conntrack-tools bash nano zip openssh-server-pam

mkdir /home/$(hostname)/.config/
mv "$(pwd)/" /home/$(hostname)/.config/

cd /home/$(hostname)/.config/voider/
wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/libqrencode-tools-4.1.1-r2.apk
wget http://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/libqrencode-4.1.1-r2.apk
apk add --allow-untrusted ./libqrencode-4.1.1-r2.apk
apk add --allow-untrusted ./libqrencode-tools-4.1.1-r2.apk
rm libqrencode-tools-4.1.1-r2.apk
rm libqrencode-4.1.1-r2.apk
wget http://dl-cdn.alpinelinux.org/alpine/v3.20/community/aarch64/tcpreplay-4.4.4-r1.apk 
apk add --allow-untrusted ./tcpreplay-4.4.4-r1.apk
rm tcpreplay-4.4.4-r1.apk

cd /home/$(hostname)/.config/voider/python/
wget https://dl-cdn.alpinelinux.org/alpine/latest-stable/community/aarch64/py3-pip-24.3.1-r0.apk
apk add --allow-untrusted ./py3-pip-24.3.1-r0.apk
rm py3-pip-24.3.1-r0.apk

python3 -m venv .
chmod +x ./bin/activate
./bin/activate
./bin/pip3 install scapy
#./bin/deactivate

cd /home/$(hostname)/.config/voider/
mv call_caller /etc/init.d/
mv call_caller.sh ../../
mv caller.sh ../../

wget https://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/tor-0.4.8.14-r0.apk
apk add --allow-untrusted ./tor-0.4.8.14-r0.apk
rm tor-0.4.8.14-r0.apk

wget https://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/tor-openrc-0.4.8.14-r0.apk
apk add --allow-untrusted ./tor-openrc-0.4.8.14-r0.apk
rm tor-openrc-0.4.8.14-r0.apk

wget https://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/torsocks-2.4.0-r0.apk
apk add --allow-untrusted ./torsocks-2.4.0-r0.apk
rm torsocks-2.4.0-r0.apk

wget https://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/shadow-4.14.2-r0.apk
apk add --allow-untrusted ./shadow-4.14.2-r0.apk
rm shadow-4.14.2-r0.apk

wget https://dl-cdn.alpinelinux.org/alpine/v3.19/community/aarch64/shadow-login-4.14.2-r0.apk
apk add --allow-untrusted ./shadow-login-4.14.2-r0.apk
rm shadow-login-4.14.2-r0.apk 


#! /bin/bash

rm -f /etc/rc.local

rm -r -f ~/.config/voider

cp /etc/ssh/sshd_config_back /etc/ssh/sshd_config

rm -f /etc/ssh/sshd_config_back

apt remove python3-pip

pip3 remove scapy

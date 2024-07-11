#! /bin/bash

# execute these lines as root first:
echo "HostKey /etc/ssh/ssh_host_ed25519_key" >> /etc/ssh/sshd_config

cp /etc/ssh/sshd_config /etc/ssh/sshd_config_back

apt install python3-pip

pip3 install scapy

#python3 mgmt.py blub

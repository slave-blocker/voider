#!/bin/bash

echo net.ipv6.conf.all.disable_ipv6=1 >> /etc/sysctl.conf
echo net.ipv6.conf.default.disable_ipv6=1 >> /etc/sysctl.conf
echo net.ipv6.conf.lo.disable_ipv6=1 >> /etc/sysctl.conf

sysctl -p

curl -L https://install.pivpn.io | bash

line_n=$(grep -n "pivpnNET=" /etc/pivpn/wireguard/setupVars.conf  | cut -d : -f1)
sed -i "$line_n s?.*?pivpnNET=172.31.0.0?" /etc/pivpn/wireguard/setupVars.conf

line_n=$(grep -n "pivpnenableipv6=" /etc/pivpn/wireguard/setupVars.conf  | cut -d : -f1)
sed -i "$line_n s?.*?pivpnenableipv6=0?" /etc/pivpn/wireguard/setupVars.conf
    
line_n=$(grep -n "Address =" /etc/wireguard/wg0.conf  | cut -d : -f1)
sed -i "$line_n s?.*?Address = 172.31.0.1/24?" /etc/wireguard/wg0.conf

rc-update add call_caller default
/etc/init.d/call_caller start

rc-update add tor default
mv /etc/tor/torrc.sample /etc/tor/torrc
/etc/init.d/tor start

reboot

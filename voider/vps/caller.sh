#! /bin/bash

python3 ./udp_server.py 1>/dev/null 2>/dev/null &
echo "udp_server.py : " $!

python3 ./doa.py 1>/dev/null 2>/dev/null &
echo "doa.py : " $!

/root/crypto_pay/btc/electrum-3.3.8-x86_64.AppImage daemon 1>/dev/null 2>/dev/null &
echo "electrum daemon : " $!

#! /bin/bash

/root/crypto_pay/btc/electrum-3.3.8-x86_64.AppImage daemon </dev/null 1>/dev/null 2>/dev/null &
echo -n $! > daemon_pid.txt

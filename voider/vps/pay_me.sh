#! /bin/bash

cp /var/sftp/newuser/newuser /root/newuser &
python3 /root/crypto_pay/btc/pay_me.py &

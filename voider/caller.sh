#! /bin/bash

sleep 60s

cd /home/§/.config/voider/

./rp_filter_off
python3 server_deamon.py 1>/dev/null 2>/dev/null &
python3 clients_deamon.py 1>/dev/null 2>/dev/null &

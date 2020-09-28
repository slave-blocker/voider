import logging
import socket
import sys
from util import *
import threading

logger = logging.getLogger()

with open("/root/users") as file :
    servers = file.read().splitlines()
file.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 6868))

while True:
    
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print('connection from: ' + str(addr[0]) + ' @port : ' + str(addr[1]) )
    pair = data.decode("utf-8").split()
    print(pair)
    
    if pair[0] in servers :
        with open('/var/sftp/' + pair[0] + '/clients') as file :
            clients = file.read().splitlines()
        file.close()
        if pair[1] in clients :
            count = 0
            while count < 24 :
                data2, addr2 = sock.recvfrom(1024)
                pair2 = data2.decode("utf-8").split()
                if pair2[0] == pair[1] and pair2[1] == pair[0]:
                    print("server - send client info to: ", addr)
                    sock.sendto(addr_and_pair_to_msg(addr2, pair2), addr)
                    print("server - send client info to: ", addr2)
                    sock.sendto(addr_and_pair_to_msg(addr, pair), addr2)
                    break
                count = count + 1
    else :
        if pair[1] in servers :
            with open('/var/sftp/' + pair[1] + '/clients') as file :
                clients = file.read().splitlines()
            file.close()
            if pair[0] in clients :
                count = 0
                while count < 24 :
                    data2, addr2 = sock.recvfrom(1024)
                    pair2 = data2.decode("utf-8").split()
                    if pair2[0] == pair[1] and pair2[1] == pair[0]:
                        print("server - send client info to: ", addr)
                        sock.sendto(addr_and_pair_to_msg(addr2, pair2), addr)
                        print("server - send client info to: ", addr2)
                        sock.sendto(addr_and_pair_to_msg(addr, pair), addr2)
                        break
                    count = count + 1
    

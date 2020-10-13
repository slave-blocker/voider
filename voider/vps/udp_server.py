import logging
import socket
import sys
from util import *
import threading

def join(sock, pair, port, servers, addr):
    
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
        return
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
        return

logger = logging.getLogger()

with open("/root/servers") as file :
    servers = file.read().splitlines()
file.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', ))

List1 = []
List2 = []
while True:
    
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
    print('connection from: ' + str(addr[0]) + ' @port : ' + str(addr[1]) )
    pair = data.decode("utf-8").split()
    print(pair)
    if pair[0] in servers or pair[1] in servers :
        if pair not in List1 :
            peer = [pair[1], pair[0]]
            if peer in List1 :
                index = List1.index(peer)
                port = List2[index]
                sock.sendto(addr_to_msg(("", port)), addr)
                del List1[index]
                del List2[index]
            else :
                meet = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
                meet.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                meet.bind(('', 0))
                port = meet.getsockname()[1]
                List1.append(pair)
                List2.append(port)
                sock.sendto(addr_to_msg(("", port)), addr)
                threading.Thread(target=join, args=(meet, pair, port, servers, addr, )).start()

# voider

Be your own phonecentral.
Make phonecalls to 10.i.s.p
   
i is the index of the network namespace .
s ist the number of the subnet, and p is the number of the phone.
   
How to install :
Download it and extract the zip. Take the resulting voider folder and put it in the 
~/.config/ directory. 
      
Look at the install.sh to see which dependency's you need. 
A rc.local example is given. The /etc/rc.local then calls a so called caller.sh at boot time.
This lets two scripts run in the background. These are the server_deamon.py ( not daemon )
and the clients_deamon.py. Also a small script called rp_filter is executed to allow forwarding and turning off rp_filter and turning on accept_local.
       
Usage :
The main.py should be executed always with :

sudo -E python3 main.py 
        
Creating new clients to our own openvpn server should be straight forward aswell as creating new clients connections to other servers. The output of main.py should be self explanatory.

Some confusion could arise from creating access credentials .
What is happening is that when a client connects to the server it does so using a vps as a rendezvous point, for the udp holepunch. So in this regard the client is a peer and the server is a peer. Each needs to know if the other is online. 
Furthermore this is a multi-cloud situation because the server might be at one vps and the client might be at another vps. And the client always connects to the server using the vps of the server.
The client already has the access credentials in the modified openvpn certificate.
But the server does not. So the client creates an access credentials file for the server.
This is a sftp read connection for only one file called DoA and stands for Dead or Alive.
The server then needs to import this access credentials file.
These are the two last options in the main.py .

On the ip phone the ip address has to be given and the respective gateway aswell. the network mask is naturally /30 .

After this a user can make direct ip calls to it's respective phone numbers. 

This means a user calls :

10.1.2.1 ---> 1st client

10.1.3.1 ---> 2nd client 

10.1.4.1 ---> 3rd client

etc

10.2.1.1 ---> 1st server 

10.3.1.1 ---> 2nd server 

10.4.1.1 ---> 3rd server

etc


No Voice mail is supported ...
Conference calls are not supported. They might be implemented in the future, if a more elaborate patch can be done to listen on the wire.
Putting calls on hold works. ( a feature of the GXP-1610 )

Currently there is no possibility of having a client-to-client connection. Therefore s=1 for every client, because every client only connects to the server. Moreover p=1, as this is targeted firstly at raspberry pi's these only have one ethernet port and thus only one phone can connect to it. This is in part because of a patch handling sip and rtp, using tcpdump to listen on the wire.
This project works with the GXP-1610, YEA SIP-T19P and it is assumed that it works with every ip phone that is able to do direct ip calls without proxy. The exchange of audio codecs seems to work fine, and is interoperable on these "new" ip phones.
The YEA SIP-T19P makes outbound calls but does not receive them. This might be tweakable on the settings of the phone via web interface. (there are a lot)

Every phone needs to have a different ip address. 

Because after sip, when the rtp stream starts it uses the addresses from the caller and the callee wich are on the phones. Besides that the ip addresses of the phones are totally irrelevant. If the phones would have the same ip address then sip works but the phone would be calling itself so it does not send the rtp packets out it's gateway.

The range of the phone numbers goes from :
172.16.0.0 to
172.28.255.252

This number is set directly on the phone itself. 
Use also, sudo -E python3 main.py, again to define the phone number aswell as the gateway.

As s ranges from 1 to 255 for a server and i ranges from 1 to 255 aswell, every user has up to 500 possible connections.

The code for the vps is also given, which includes the creation and deletion of sftp users for read and write and only read. And also a script that joins two peers using udp sockets.

General comments and instructions for using my vps are given in "notes" .

please do contact me for critics, suggestions, questions, kudos, and even mobbing attempts are welcome.

@ irc
monero-pt

special thanks to Andreas Hein

a do nation is the best nation

BTC :

bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv

![What is this](btc.gif)

MONERO :

48kABkceuv98L51VCDZTqLfhUyAEd15aZZkAifxvU61kWHdqMKghmfD6ND3tKx1euBaCYUwsPLxE4MVHkHb3qDgb7ESycc1

and decentralized google is doodle 

:)

# voider

Be your own phonecentral.
Make phonecalls to 10.i.s.p
   
i is the index of the network namespace .
s ist the number of the subnet, and p is the number of the phone.
   
How to install :
Download it and extract the zip. Take the resulting voider folder and put it in the 
~/.config/ directory. 
   
Delete all the "blub" files in the sub directories, git does not handle well the empty directories.
So these files had to be included such that i was able to upload the needed directory tree.
       
Look at the install.sh to see which dependency's you need. 
a rc.local example is given. The /etc/rc.local then calls a so called caller.sh at boot time.
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
This project works with, and was only tested so far with the GXP-1610, an ip phone from Grandstream.
Other phones that work with this system are unknown to me. 
Every phone needs to have a different ip address. Because after sip, when the rtp stream starts it uses the addresses from the caller and the callee wich are on the phones. Besides that the ip addresses of the phones are totally irrelevant. If the phones would have the same ip address then sip works but the phone would be calling itself so it does not send the rtp packets out it's gateway.

The range goes from :
172.16.0.0 to
172.28.255.252

As s ranges from 1 to 255 for a server and i ranges from 1 to 255 aswell every user has up to 500 connections. Now because of the birthday's paradox :

The range implies 13 * ( 2 ^ 16 ) addresses .
13 because 13 = (28 - 16) + 1 .
so 13 * ( 2 ^ 16 ) = 851968 addresses .
Because we are dealing with /30 we divide by 2 
having 425984 usable addresses one for the phone and one for the gateway.
Now as we are dealing with sets just as with days we divide by 2 again.
having 212992 networks. Now if instead of 365 days we would have 212992 days, then if there are 544 phones in the system that choose their ip address randomly then it is likely that there will be two that will have the same ip address.

This could be addressed in two ways adopting ipv6 in a future version having the tradeoff that an user might need to call numbers such as fd68:cafe:beef:dead:feeb:feed:deaf:face wich could become a burden. Or every user asks it's 500 connected servers and clients : does someone have the same ip for the phone? And if yes then that gets resolved . Notice how when a user is connected to 255 servers and has 255 clients every one of them can use the same ip address on the phone. Because it is not transitive, there is no client to client connection, this should be fine.

The code for the vps is also given, which includes the creation and deletion of sftp users for read and write and only read. And also a script that joins two peers using udp sockets.

If wireshark is not lying and the dlp is not broken for the elliptic curves used by openvpn and if your linux os has no backdoor circumventing wireshark. Then you can use voip in openvpn using up to 512 bits of security.
No need to use anything else to do international phonecalls.
It works fine and feels great. No third parties besides the vps that is helping with the holepunch.
This project is also great for someone that wishes to learn how to code since it contains all the basics, without pointers...

In the unlikely case that you are reading this, and in the even more unlikely case that you are baffled in amazement.
you can use my cloud if you want and are willing to pay .

1) gpg --full-generate-key

in here, give your user name, or "uid". Let's say it's bob.

2) gpg --export --armor --output newuser bob

3) connect to my cloud over sftp.

sftp newuser@192.236.162.238
pass : q2YtGlaKjd3wJ

4) get address

4)Ö)
   bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv
   is just an example address, that you would find in the text file called address.
   You then take that address and put it in the 2nd line of the newuser file.

5) edit the newuser file, which contains your public key.
   as such :
 
   bob<br/>
   bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv<br/>
   yourpublickey

5)Ö)
   This means, the text file "newuser" . Shall be edited as follows :
   
   bob (Line 1 of text file) <br/>
   bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv (Line 2 of text file) <br/>
   yourpublickey (starting from line 3 until the end of text file)

6) put newuser

7) transact 0.0012 btc to the given address. You have 3 hours to have it confirmed.

8) After confirmation, a file with that address name will be @ newuser@192.236.162.238

9) get bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv

10) gpg --output creds --decrypt bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv

11) now your credentials are with you, you can type them in when using 

sudo -E python3 main.py

Your credentials will be deleted after 4 hours.
only one payment can be processed every 3 hours. 
Does that mean that you can write a script that will use paramiko to spoof it, so it does not work?
Yes, you can. 


The next milestone is to achieve udp holepunching through tor.

please do contact me for critics, suggestions, questions, kudos, and even mobbing attempts are welcome.

@ irc
monero-pt

special thanks to Andreas Hein

a do nation is the best nation

BTC :

bc1qgpschlf2hrv2pgthdq52ksurnwaqzn7kk9pupv

MONERO :

48kABkceuv98L51VCDZTqLfhUyAEd15aZZkAifxvU61kWHdqMKghmfD6ND3tKx1euBaCYUwsPLxE4MVHkHb3qDgb7ESycc1

and decentralized google is doodle 

:)

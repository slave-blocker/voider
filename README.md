# voider

Be your own phonecentral.
Make phonecalls to 10.i.s.p

i is the index of the network namespace .
s ist the number of the subnet, and p is the number of the phone.

How to install :
Download it and extract the 

The rendezvous point is a vps.
Currently there is no possibility of having a client-to-client connection. Therefore s=1 for every client, because every client only connects to the server. Moreover p=1, as this is targeted firstly at raspberry pi's these only have one ethernet port and thus only one phone can connect to it. This is in part because of a patch handling sip and rtp, using tcpdump to listen on the wire.
This project works with, and was only tested so far with the GXP-1610, an ip phone from Grandstream.
Other phones that work with this system are unknown to me. Every phone needs to have a different ip address. The range goes from :
172.16.0.0 to
172.28.255.252

As s ranges from 1 to 255 for a server and i ranges from 1 to 255 aswell every user has up to 500 connections. Now because of the birthday's paradox :

The range implies 13 * ( 2 ^ 16 ) addresses .
13 because 13 = (28 - 16) + 1 .
so 13 * ( 2 ^ 16 ) = 851968 addresses
Because we are dealing with /30 we divide by 2 
having 425984 usable addresses one for the phone and one for the gateway.
Now as we are dealing with set's just as with day's we divide by 2 again.
having 212992 networks. Now if instead of 365 days we would have 212992 days, then if there are 544 phones in the system that choose their ip address randomly then it is likely that there will be two that will have the same ip address.
This could be addressed in two ways adopting ipv6 in a future version having the tradeoff that user might need to call numbers such as fd68:cafe:beef:dead:feeb:feed:deaf:6870 wich could become a burden. Or every user asks it's 500 connected servers and clients : does someone have the same ip for the phone? And if yes then that gets resolved . Notice how when a user is connected to 255 servers and has 255 clients every one of them can use the same ip address on the phone. Because it is not transitive, there is no client to client connection, this should be fine.



a do nation is the best nation
49k9fez67M6JLmkyveQvQFKjZNBsfi6VsS363pYBKqG8ekuUQXFbR8LZ7mv7R57H4hMnMCK7BdcwCFHxuGuHcZ1NN3gJdPD

and decentralized google is doodle 

:)

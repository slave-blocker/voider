# voider

![tiefer](tiefer.png)


Direct Ip Calls, wich are ip agnostic.\
srtp is natively supported by the phones.\
the private phone number on the phone itself is always : **172.16.19.85/30**\
the gateway is always : **172.16.19.86/30**.

(agnostic in the sense that on the good old phones you did not know who was calling you,\
because old phones don't have a display. So it's _i got to hear it to believe it_ you will\
see the call incoming from a specific fake ip address but you may or may not map that to\
the callers ip address. So perhaps anonymous phone calls is a better term :)

Disclaimer : 
You need to already be using a linux machine to set this up.
You need to know how to ssh into a linux machine to set this up.
After all is done this raspi will be a device to be thought of like the good old phones,
as seen on the picture. This raspi will be a dedicated machine only for the phone.
This software is based on the assumption that source ports are not filtered/changed outwards
which is the case for most retail routers.


**How to install** :

flash alpine linux :

dd if=alpine-rpi-3.20.3-aarch64.img of=/dev/sdX bs=4M

run setup-alpine

setup another user other than root, dhcp on eth0 is fine.

choose UTC as the timezone and chrony. This is crucial such that all devices are synced on the same timeline.

use the same micro sd card for the os (type mmcblk0).

* make sure to have a ssh cert to login to your raspi before continuing *
* and do login before continuing, with that cert into the raspi a couple of times *
* or else you might get locked out of the raspi once setup is done *

git clone https://github.com/slave-blocker/voider.git

cd voider/voider

as user :

doas ./install.sh

as root :

(let it be wireguard, let quad9, no to ipv6 and at the end don't reboot, the script will do that for you)

./install_as_root.sh

**How to setup** :

~/$ cd .config/voider

choose interfaces :

(this will setup /etc/network/interfaces and then reboot)
(the phone needs to be connected already with the raspi)

after this reboot :
~/$ cd .config/voider

doas ./main.sh

this will setup the sftp connections over tor.
once executing doas ./main.sh returns the available options you should be good to go.

**How to use** :

Buy a Grandstream IP phone, that has a Direct ip call feature. (tested with GXP1610)

Install voider on a Raspberry Pi, or any Linux machine.

Connect a Grandstream phone to the usb dongle of your machine.

Run : 

doas ./main.sh

to create new clients or to connect to servers.
  
Once connections exist to servers or clients,
go to the phone and DIRECT IP CALL : 

10.1.2.1 ---> 1st client

10.1.3.1 ---> 2nd client 

10.1.4.1 ---> 3rd client

etc

10.2.1.1 ---> 1st server 

10.3.1.1 ---> 2nd server 

10.4.1.1 ---> 3rd server

etc

_Out of the box Grandstream phones should use rtp, to enable srtp, access your phones web interface
and go to account -> audio settings and put srtp -> Enabled and forced_.

**There is no pbx being used, instead sip packets die before getting to the callee.
And then some deep packet inspection happens. Replacing the 172.16.19.85 by a fake address.
The packet is then replayed, by scapy and tcprewrite, towards the callee phone.**

**Note**

A server passes its cert for the sftp over tor, for its clients to connect with torsocks.
A client with that cert can only enter the raspi by sftp. The only login shell available for 
this user in question called "self" is : /bin/false.
Once he logs into the sftp chroot dir /var/sftp/self/ he can only write to the files he sees with ls.
And only up to 2KB. The amount of processes made available for self on the server are 8 
(should be 2 per sftp connection), meaning  only 4 sftp connections at the same time can happen.
This is not a problem since torify sftp for read and write are only a few seconds. 

* making voider mobile, this is letting you just plug it off and turning it on, in another house 
behind a different router with no configuration on your part is coming soonTM *

Please do contact me for critics, suggestions, questions, kudos, and even mobbing attempts are welcome.

Remember if your hardware is backdoored anyway, backdoored you are...

@ irc   **monero-pt**

special thanks to Andreas Hein !

A do nation is the best nation !

**MONERO** :

![xmr](xmr.gif)


# voider

Be your own phonecentral.
Make phonecalls to 10.i.s.p !
   
The index of the network namespace is i,
s is the number of the subnet, and p is the number of the phone.
   
**How to install** :
 
git clone https://github.com/slave-blocker/voider.git

cd voider/voider

Run the install with the user that is going to have the scripts,
in /home/(you)/.config/

./install.sh (sudo password will be needed)      

**How to use** :

Buy a GXP1610 IP phone.

Install voider on a Raspberry Pi, or any Linux machine.

Connect the GXP1610 to the ethernet port of your machine.

Run : 

sudo -E python3 main.py

to create new clients or to connect to servers.
Also define your phone number and gateway etc.  
  
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

General comments and instructions are given in "notes" .



Please do contact me for critics, suggestions, questions, kudos, and even mobbing attempts are welcome.

@ irc   **monero-pt**

special thanks to Andreas Hein !

a do nation is the best nation !

**BTC** :

![btc](btc.gif)

**MONERO** :

![xmr](xmr.gif)

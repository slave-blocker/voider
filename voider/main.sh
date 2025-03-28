#!/bin/bash

if [[ $EUID != 0 ]]
    then
    echo "run this part with doas"
    exit 1
fi

home="/home/"$(hostname)"/"

intin=$home".config/voider/self/int_in"

if [[ ! -e $intin ]]
    then
    echo "Incoming interface not defined, the one connected to the phone ."
    ls "/sys/class/net"
    echo "Please type one from the above list :"
    read int_in
    echo -n $int_in > $intin 
fi

intout=$home".config/voider/self/int_out"

if [[ ! -e $intout ]]
    then
    echo "Outgoing interface not defined, the one directed to the internet ."
    ls "/sys/class/net"
    echo "Please type one from the above list :"
    read int_out
    echo -n $int_out > $intout 
fi

localip=$home".config/voider/self/localip"

if [[ ! -e $localip ]]
    then
    echo "setting a permanent lan ip, with dhcp"
    echo "checking for a connection, pinging google"    
    ping -c 1 8.8.8.8                    
    if [[ $? -eq 0 ]]       
        then
        echo "assuming "$(cat $intout)" is connected to the internet"
        lanip=$(ip -f inet addr show $(cat $intout) | awk '/inet / {print $2}')    

        sed -i "s%§0%$(cat $intout)%g" $home".config/voider/self/interfaces"        
        sed -i "s%§1%$(cat $intin)%g" $home".config/voider/self/interfaces"        
        sed -i "s%§2%address\ $lanip%g" $home".config/voider/self/interfaces"

        lanip=$(ip -f inet addr show $(cat $intout) | sed -En -e 's/.*inet ([0-9.]+).*/\1/p')    

        echo -n $lanip > $localip

        doas mv $home".config/voider/self/interfaces" "/etc/network/interfaces"
        echo " making changes to the interfaces permanent, rebooting ..."
        doas reboot
        exit 1   
    else
        echo "Please get an ip address over dhcp for "$(cat $intout)
        exit 1   
    fi
fi

self_dir="/home/self"

if [[ ! -e $self_dir ]]
    then   
/home/$(hostname)/.config/voider/sftp_setup 1
fi

echo "choose option :"

echo "to quit - just press enter."
echo "1 - call pivpn, to add a client connection to this server"
echo "2 - call pivpn, to revoke a client connection to this server"
echo "3 - create a client connection to another server"
echo "4 - delete a client connection to another server"
echo "5 - show own onion"

#TODO echo "6 - shutdown entire network routing protocol"


read option

if [[ $option -eq 1 ]]
    then

    #the server here chooses the x in 10.1.x.1 

    pivpn -a

    #this line is crucial since the wireguard server needs to let 172.29.0.0/16 pass.

    lines=$(cat /etc/wireguard/wg0.conf | wc -l)    
    lines=$(( $lines - 1 ))   
    #this always works because wireguard appends its clients to wg0.conf
    crucial=$(echo  $(sed "$lines q;d" /etc/wireguard/wg0.conf ), 172.29.0.0/16)
    sed -i "$lines s?.*?$crucial?" /etc/wireguard/wg0.conf
    wg-quick down wg0
    wg-quick up wg0
    
    certdotconf=$(ls /home/$(hostname)/configs)

    str=$(sed "3 q;d" /home/$(hostname)/configs/$certdotconf)
    str2=$(echo $str | sed 's/\/.*//')
    client_idx=$(echo $str2 | awk -F'.' '{print $4}')

    sed -i "$client_idx s/.*/1/" /home/$(hostname)/.config/voider/clients/occupants 
    mkdir /home/$(hostname)/.config/voider/clients/clients/$client_idx
    mkdir /home/$(hostname)/.config/voider/clients/clients/$client_idx/cert/
    
    rm -rf /home/$(hostname)/.config/voider/new_client/
    mkdir /home/$(hostname)/.config/voider/new_client/
    
    mkdir /home/$(hostname)/.config/voider/new_client/cert
    mv /home/$(hostname)/configs/$certdotconf /home/$(hostname)/.config/voider/new_client/cert
    echo "PersistentKeepalive = 5" >> /home/$(hostname)/.config/voider/new_client/cert/$certdotconf
    cp /home/$(hostname)/.config/voider/new_client/cert/$certdotconf /home/$(hostname)/.config/voider/clients/clients/$client_idx/cert/$certdotconf

    touch /var/sftp/self/$client_idx
    chown self:self /var/sftp/self/$client_idx
    chmod 600 /var/sftp/self/$client_idx 

    mkdir /home/$(hostname)/.config/voider/new_client/sftp/
    cp /home/$(hostname)/.config/voider/self/sftp/self /home/$(hostname)/.config/voider/new_client/sftp/self
    
    host_hash=$(cat /etc/ssh/ssh_host_ed25519_key.pub)
    onion=$(cat /home/$(hostname)/.config/voider/self/onion)
    echo $onion $host_hash > /home/$(hostname)/.config/voider/new_client/sftp/host.pub

    mkdir /home/$(hostname)/.config/voider/new_client/tor/
    cp /home/$(hostname)/.config/voider/self/onion /home/$(hostname)/.config/voider/new_client/tor/onion
        
    cd /home/$(hostname)/.config/voider/new_client/
    # this is given through a secured channel to the client :
    zip -m -r client_certs.zip .

    echo "client created, to be called @ 10.1.$client_idx.1"
    echo "pass client_certs.zip in /home/$(hostname)/.config/voider/new_client/ through a secured channel to the client."

fi

if [[ $option -eq 2 ]]
    then
    echo "Please choose x ( 2<= x <= 254), to remove phone number : 10.1.x.1 "
    echo "Press enter when done."
    read x
        
    if [[ $x -lt 2 ]] || [[ $x -gt 254 ]]
        then
        echo "Please try again"
        exit
    fi

    str=$(sed "$x q;d" /home/$(hostname)/.config/voider/clients/occupants)
    
    if [[ $str -eq "0" ]]
        then
        echo "Phone number does not exist"
        exit
    else    
        #this directory only contains one file :
        certdotconf=$(ls /home/$(hostname)/.config/voider/clients/clients/$x/cert/)
        client_name=$(echo $certdotconf | sed 's/\..*//')
        pivpn -r $client_name -y
        rm -rf /home/$(hostname)/.config/voider/clients/clients/$x
        rm /var/sftp/self/$x
        sed -i "$x s/.*/0/" /home/$(hostname)/.config/voider/clients/occupants
        echo "phone number deleted."    
    fi
fi

if [[ $option -eq 3 ]]
    then
    echo "Please place the client_certs.zip into the folder \"new_server\" "
    echo "Press enter when done."
    read

    certdotconf=$(ls /home/$(hostname)/.config/voider/new_server)

    if [[ -z $certdotconf ]]
        then
        echo "Please try again"
        exit
    fi

    echo "Please choose x ( 2<= x <= 254) with which number to call : 10.x.1.1 "
    echo "Press enter when done."
    read x
        
    if [[ $x -lt 2 ]] || [[ $x -gt 254 ]]
        then
        echo "Please try again"
        exit
    fi

    str=$(sed "$x q;d" /home/$(hostname)/.config/voider/servers/occupants)
    
    if [[ $str -ne "0" ]]
        then
        echo "Phone number already taken"
        exit
    fi

    #unzip here, and copy the respective certs.
    cd /home/$(hostname)/.config/voider/new_server/

    unzip client_certs.zip
    rm client_certs.zip       
    
    #check for wg cert
    if [[ ! -e /home/$(hostname)/.config/voider/new_server/cert ]]
        then        
        echo "fail, no wg dir"
        exit 1
    fi    

    #check for onion
    if [[ ! -e /home/$(hostname)/.config/voider/new_server/tor/onion ]]
        then        
        echo "fail, no onion"
        exit 1
    fi

    #check for sftp cert
    if [[ ! -e /home/$(hostname)/.config/voider/new_server/sftp/self ]]
        then        
        echo "fail, no sftp cert"
        exit 1
    fi

    mkdir /home/$(hostname)/.config/voider/servers/servers/$x/
    
    mv /home/$(hostname)/.config/voider/new_server/* /home/$(hostname)/.config/voider/servers/servers/$x/

    sed -i "$x s/.*/1/" /home/$(hostname)/.config/voider/servers/occupants 

    echo "phone number added."

fi

if [[ $option -eq 4 ]]
    then
    echo "Please choose x ( 2<= x <= 254), to remove phone number : 10.x.1.1 "
    echo "Press enter when done."
    read x
        
    if [[ $x -lt 2 ]] || [[ $x -gt 254 ]]
        then
        echo "Please try again"
        exit
    fi

    str=$(sed "$x q;d" /home/$(hostname)/.config/voider/servers/occupants)
    
    if [[ $str -eq "0" ]]
        then
        echo "Phone number does not exist"
        exit
    else    
        rm -rf /home/$(hostname)/.config/voider/servers/servers/$x
        sed -i "$x s/.*/0/" /home/$(hostname)/.config/voider/servers/occupants
        echo "phone number deleted."    
    fi
fi

if [[ $option -eq 5 ]]
    then
    cat /home/$(hostname)/.config/voider/self/onion
    echo " "
fi


# voider

![tiefer](tiefer.png)

---

**Direct IP Calls** - IP agnostic.

- **SRTP** is natively supported by the phones.
- The private phone number on the phone itself is always: **172.16.19.85/30**
- The gateway is always: **172.16.19.86/30**.

*Note:* Agnostic in the sense that on the good old phones, you did not know who was calling you, because old phones don't have a display. So it's _I got to hear it to believe it_. You will see the call incoming from a specific fake IP address, but you may or may not map that to the caller's IP address. So perhaps "anonymous phone calls" is a better term. There is a "do not disturb" feature which you can use; the phone stays quiet, and the caller gets a "busy" signal. :)

---

## Disclaimer

- You need to already be using a **Linux machine** to set this up.
- You need to know how to **SSH** into a Linux machine to set this up.

After all is done, this Raspberry Pi will be a device to be thought of like the good old phones, as seen in the picture. This Raspberry Pi will be a dedicated machine only for the phone. This software is based on the assumption that source ports are not filtered/changed outwards, which is the case for most retail routers.

---

## How to Install

1. **Flash Alpine Linux:**

   ```bash
   dd if=alpine-rpi-3.20.3-aarch64.img of=/dev/sdX bs=4M
   ```

2. **Run `setup-alpine`.**

3. **Setup another user other than root; DHCP on eth0 is fine.**

4. **Choose UTC as the timezone and chrony.** This is crucial so that all devices are synced on the same timeline.

5. **Use the same micro SD card for the OS (type mmcblk0).**

   - *Make sure to have an SSH cert to log in to your Raspberry Pi before continuing.*
   - *Log in with that cert into the Raspberry Pi a couple of times, or else you might get locked out once setup is done.*

6. **Clone the repository:**

   ```bash
   git clone https://github.com/slave-blocker/voider.git
   ```

7. **Navigate to the directory:**

   ```bash
   cd voider/voider
   ```

8. **As user:**

   ```bash
   doas ./install.sh
   ```

9. **As root:**

   - (Let it be WireGuard, let Quad9, no to IPv6, and at the end, don't reboot; the script will do that for you.)

   ```bash
   ./install_as_root.sh
   ```

---

## How to Setup

1. Navigate to the configuration directory:

   ```bash
   ~/$ cd .config/voider
   ```

2. **Choose interfaces:**

   ```bash
   doas ./main.sh
   ```
   
   - (This will set up `/etc/network/interfaces` and then reboot.)
   - (The phone needs to be connected already with the Raspberry Pi.)

3. **After this reboot:**

   ```bash
   ~/$ cd .config/voider
   ```

4. **Run the main script again:**

   ```bash
   doas ./main.sh
   ```

   This will set up the SFTP connections over Tor. Once executing `doas ./main.sh` returns the available options, you should be good to go.

---

## How to Use

1. **Buy a Grandstream IP phone** that has a Direct IP call feature (tested with GXP1610).

2. **Install voider on a Raspberry Pi or any Linux machine.**

3. **Connect a Grandstream phone to the USB dongle of your machine.**

4. **Run:**

   ```bash
   doas ./main.sh
   ```

   to create new clients or to connect to servers.

5. **Once connections exist to servers or clients, go to the phone and DIRECT IP CALL:**

   - **Clients:**
     - 10.1.2.1 ---> 1st client
     - 10.1.3.1 ---> 2nd client
     - 10.1.4.1 ---> 3rd client
     - etc.

   - **Servers:**
     - 10.2.1.1 ---> 1st server
     - 10.3.1.1 ---> 2nd server
     - 10.4.1.1 ---> 3rd server
     - etc.

*Out of the box, Grandstream phones should use RTP. To enable SRTP, access your phone's web interface and go to Account -> Audio Settings and set SRTP to Enabled and Forced.*

---

## Important Note

A server passes its certificate for the SFTP over Tor, allowing its clients to connect with torsocks. A client with that certificate can only enter the Raspberry Pi via SFTP. The only login shell available for this user, called "self," is: `/bin/false`. Once logged into the SFTP chroot directory `/var/sftp/self/`, the user can only write to the files they see with `ls`, and only up to 2KB. The number of processes available for "self" on the server is 8 (should be 2 per SFTP connection), meaning only 4 SFTP connections can happen at the same time. This is not a problem since Torify SFTP for read and write operations typically only takes a few seconds.

*Making voider mobile means you can just unplug it and turn it on in another house behind a different router with no configuration on your part. This feature is coming soon™.*

---

## Contact

Please do contact me for critiques, suggestions, questions, kudos, and even mobbing attempts are welcome.

Remember, if your hardware is backdoored anyway, backdoored you are...

@ IRC: **monero-pt**

Special thanks to Andreas Hein!

A donation is the best nation!

---

## **MONERO**

![xmr](xmr.gif)


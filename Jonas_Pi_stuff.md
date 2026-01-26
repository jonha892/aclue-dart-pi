# Initial scripts

Readme file for when Bookstacks documentation is un available.

## Prerequisites

- SD card (minimum 8GB)
- Tool to flash SD Card (e.g. [Balena etcher](https://www.balena.io/etcher/))
- [Raspberry Pi OS](https://www.raspberrypi.org/software/operating-systems/)
- Generate a new password for the pi user of the Pi (but since password login will be disabled this
  will not be used later so it should not matter)
- Generate an SSH key pair if you do not already have one
- Prepare the acloud password and Gitea username and password

## Setup

1. Flash the downloaded OS onto the SD card
2. Open the SD card in a file explorer and add an empty file with the file name `ssh` into the root
   of the SD card
3. Put the SD card into the Raspberry Pi and connect the Pi to power and your router
4. Wait for it to start and connect to it using PuTTY

## Generate SSH key pair

If you do not already have one then do the following:

**TODO**

## PuTTY connection

If you have already setup the pi once using SSL certificates and your router automatically assigns
it the same IP address, it should be reachable via the old shortcut.

### New shortcut

1. Open PuTTY
2. Assign the hostname using `pi@`HOSTNAME
3. Under `Connection` --> `SSH` --> `Auth` supply the key
4. Save the config under the same name as the HOSTNAME
5. Create a shortcut to the `putty.exe`
6. Right-click and select Properties
7. Under `Shortcut` add the following to the target  
   `-load `HOSTNAME

### Old shorcut

Accept the PuTTY Security Alert with "Yes" and wait for the connection.  
The SSL key will be refused so login using `raspberry` as password.


# Commands on pi

## Change hostname
sudo hostnamectl set-hostname "HOSTNAME"

## Configure passwordless SSH access
install -d -m 700 ~/.ssh
Paste generated public SSH key into following file: ~/.ssh/authorized_keys
sudo chmod 644 ~/.ssh/authorized_keys
sudo chown pi:pi ~/.ssh/authorized_keys
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config


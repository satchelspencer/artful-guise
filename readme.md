## Architecture
The video triggering system is composed of a number of raspberry pi zero w's, one running as an access point that all the others join. A control computer also connects to that network and will recieve OSC messages to control resolume and the video output. Each individual pi broadcasts OSC, so the ips do not have to be statically assigned.

## Installation

### Raspian For all Pi's
 - download [noobs](https://www.raspberrypi.org/downloads/) (2.4.5)
 - format an sd card using [this formatter](https://www.sdcard.org/downloads/formatter_4/) set the volume name to boot and ms-dos format
 - put the contents of the noobs installer onto the card
 - boot the pi and let the install run. 20-40min

### Access Point Pi setup
using dnasmasq and hostapd. based on [this tutorial](https://www.raspberrypi.org/documentation/configuration/wireless/access-point.md).

 - install dnsmasq (dhcp/routing) and hostapd (access point control).  
`sudo apt-get install dnsmasq hostapd` (will show some errors since we have no config yet. thats ok)

 - Give it a static ip (192.168.0.1): edit `/etc/dhcpcd.conf`. end of file should look like:

    ~~~
    interface wlan0
        static ip_address=192.168.0.1/24
    ~~~
    
 - Setup dhcp interface and address range: edit `/etc/dnsmasq.conf`:
 
    ~~~
    interface=wlan0      # Use the require wireless interface -                     usually wlan0
        dhcp-range=192.168.0.2,192.168.0.100,255.255.255.0,24h
    ~~~
    
 - Setup access point settings. edit/create `/etc/hostapd/hostapd.conf` 
    
    ~~~
    interface=wlan0
    driver=nl80211
    ssid=ArtfulGuise
    hw_mode=g
    channel=7
    wmm_enabled=0
    macaddr_acl=0
    auth_algs=1
    ignore_broadcast_ssid=0
    wpa=2
    wpa_passphrase=your_passphrase
    wpa_key_mgmt=WPA-PSK
    wpa_pairwise=TKIP
    rsn_pairwise=CCMP
    ~~~
    
 - set hostapd conf location to be the file we just created. edit `/etc/default/hostapd`:
   
   ~~~
   #DAEMON_CONF...
   ~~~
   becomes
   
   ~~~
   DAEMON_CONF="/etc/hostapd/hostapd.conf"
   ~~~
   
 - restartd dhcp, and access point:
    
    ~~~
    sudo service hostapd start  
    sudo service dnsmasq start  
    ~~~
 - enable routing: edit `/etc/sysctl.conf` and uncomment:
 
    ~~~
    net.ipv4.ip_forward=1
    ~~~
 - Reboot the pi. Note the ssid "ArtfulGuise" will become available before the network actually is, if you connect and can't ssh into the pi, diconnect, wait a minute and try again.

- `ssh pi@192.168.0.1`

### All Pi Hardware setup
 - using [mfrc522](https://www.nxp.com/docs/en/data-sheet/MFRC522.pdf) card reader.
 - Pins are as follows:
 
  | purpose     | rc522 pin label | pi pin number |
  |-------------|-----------------|---------------|
  | chip select | sda             | 24            |
  | clock       | sck             | 23            |
  | serial out  | mosi            | 19            |
  | serial in   | miso            | 21            |
  | interrupt   | irq             | 12            |
  | ground      | gnd             | 6             |
  | reset       | rst             | 7             |
  | 3.3v rail   | 3.3v            | 1             |
  
 - dont fuck up the soldering

### All Pi software setup
- boot the pi or pi's and connect to the internet via your home network.
- install python deps:
 - `sudo pip install pyOSC`
 - `sudo pip install pi-rc522`
- in pi's home directory clone this repo
- create a serivce in `/etc/systemd/system/art.service`
  
  ~~~
    [Unit]
    Description=RFID Scanner to OSC
    After=network.service

    [Service]
    ExecStart=/usr/bin/python scanner.py
    WorkingDirectory=/home/pi/artful-guise
    StandardOutput=inherit
    StandardError=inherit
    Restart=always
    RestartSec=5
    StartLimitInterval=600
    StartLimitBurst=100
    User=pi


    [Install]
    WantedBy=multi-user.target
  ~~~
 - enable the service at startup `sudo systemctl enable art`
 - start the service `sudo service art start`

### Connecting to pi over network.
 - boot the host pi. and other pi's. wait for access point to be available, then wait a bit more.
 - scan for pi's `nmap -sn 192.168.0.0/24`
 - you'll see 192.168.0.N, 1 being the host, one of them being your machine and the rest being other pi's

### Testing
 - ssh into the pi
 - stop the art service `sudo service art stop`
 - run it `python artful-guise/scanner.py`
 - will show card ids, and OSC urls if all is working if all is working
 - mapping of ids to osc urls is in `mapping.json` and may be changed for each pi
 - restart the service or reboot when done
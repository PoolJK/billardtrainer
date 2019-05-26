### Script to be run on the Raspberry Pi

On PC `../billardtrainer.py` initialises a table sim, loading images taken from the PiCamera over the table.    
The table sim can manage the classes under development like camera, beamer and ball.  
The camera is simulated via loaded images, the beamer is unchanged.  
Both are superimposed over the table_image.

# Setup:

Set Pythonpath:  
`sudo nano /etc/bash.bashrc`  
add:  
`export PYTHONPATH="${PYTHONPATH}:/home/pi/billardtrainer"`

### Bluetooth:

on Pi:  
install bluetooth dependencies:  
```
sudo apt-get install bluetooth libbluetooth-dev
sudo python3 -m pip3 install pybluez
```

copy `/lib/systemd/system/bluetooth.service` to `/etc/systemd/system/bluetooth.service`

create two new files:  
first  
`sudo nano /etc/systemd/system/var-run-sdp.path`  
add content:  
```
[Unit]
Description=Monitor /var/run/sdp

[Install]
WantedBy=bluetooth.service

[Path]
PathExists=/var/run/sdp
Unit=var-run-sdp.service
```
second:  
`sudo nano /etc/systemd/system/var-run-sdp.service`  
add content:  
```
[Unit]
Description=Set permission of /var/run/sdp

[Install]
RequiredBy=var-run-sdp.path

[Service]
Type=simple
ExecStart=/bin/chgrp bluetooth /var/run/sdp
```
edit bluez service:  
`sudo nano /etc/systemd/system/dbus-org.bluez.service`  
change this line:  
`ExecStart=/usr/lib/bluetooth/bluetoothd`  
to this:  
`ExecStart=/usr/lib/bluetooth/bluetoothd --compat`  
reload and enable all services:    
```
sudo systemctl daemon-reload
sudo systemctl enable var-run-sdp.path
sudo systemctl enable var-run-sdp.service
```
reboot the Pi  

PyCharm:  
`pip install pybluez-0.22-cp37-cp37m-cp37/m-win_amd64.whl`  
(from https://github.com/pybluez/pybluez/issues/180)

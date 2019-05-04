### Script to be run on the Raspberry Pi

Currently development in this branch is focused on `detect_test.py`.  
`detect_test.py` gets called via the main entry point `../billardtrainer.py`, when flag `-pc` is set.
It then initializes a Camera, calibrates it and then runs detection on the input specified, using
the classes in `../classes`.

`main.py` is merged from master-branch.

Set Pythonpath:  
`sudo nano /etc/bash.bashrc`  
add:  
`export PYTHONPATH="${PYTHONPATH}:/home/pi/billardtrainer"`

### Bluetooth:

on Pi:  
install bluetooth dependencies:  
```
sudo apt-get install bluetooth libbluetooth-dev
sudo python3 -m pip install pybluez
```
edit bluez service:  
`sudo nano /etc/systemd/system/dbus-org.bluez.service`  
change this line:  
`ExecStart=/usr/lib/bluetooth/bluetoothd`  
to this:  
`ExecStart=/usr/lib/bluetooth/bluetoothd --compat`  
restart bluetooth:  
`sudo systemctl daemon-reload && sudo systemctl restart bluetooth`  
change permissions on /var/run/sdp:  
`sudo chmod 777 /var/run/sdp`  

PyCharm:  
`pip install pybluez-0.22-cp37-cp37m-cp37/m-win_amd64.whl`  
(from https://github.com/pybluez/pybluez/issues/180)

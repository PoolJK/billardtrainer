## Software in the project

Usage in development branch (working folder = `/billardtrainer/software/`):  
`(python) billardtrainer.py [-h] [-f FILENAME] [-c] [-cf CAL_FILENAME] [-sr RES] [-dr RES] [-pc] [-ui] [-d]
 [-push] [-mir] [-test] [-p]`

optional arguments:  
  ```
  -h, --help            show this help message and exit
  -f FILENAME, --file FILENAME
                        input (device, file, video, stream)
  -c, --calibrate       perform calibration instead of loading
  -cf CAL_FILENAME      input for calibration (device, file, video, stream)
  -sr RES               source resolution
  -dr RES               display resolution
  -pc                   for testing on pc
  -ui                   use user interface, assumes -pc      # currently not functional
  -d, --debug           show more debug output
  -push, --push-to-pi   push sources to pi and run there  
  -mir, --mirror        mirror input
  -test, --camera-test  only test specified input
  -p, --preview         only show preview
  ```  
The `-push` command uses GitPython to send only modified files to the Pi. The Pi has to be reachable
via network under the alias `raspberrypi`.  
On Windows 10, PuTTY and PSCP are required to use this function, remember to add PSCP to PATH
in environment variables

example run configurations (also use .idea folder in pycharm):  
```  
billardtrainer.py -pc -res 1280x720
billardtrainer.py -pc -f http://192.168.0.59:8080/video -pc -d  
billardtrainer.py -f resources/20190405_172601.jpg -cf resources/experimental/20190405_172601.jpg -d -pc  
billardtrainer.py -f resources/20190405_172601.jpg -cf resources/experimental/cal_1.jpg,resources/experimental/cal_2.jpg,resources/experimental/cal_3.jpg -d -pc -res 800,450  
```

To find available resolutions of the camera, use flag -test, to output the resolutions to terminal.  
On the pi, try 'v4l2-ctl --list-formats-ext' (sudo apt-get install v4l-utils" if not installed).

#### classes/
Classes for the system parts

#### raspy/
Script(s) to be run on the Raspberry-Pi.  
See the readme.md for details

#### resources/
Folder for all non-code files.

#### test_ui/
A script for development convenience, possibly extendable to actual UI.  
Currently not in use

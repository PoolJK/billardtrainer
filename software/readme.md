## Software in the project

Usage in development branch (working folder = `/billardtrainer/software/`):  
`(python) billardtrainer.py [-h] [-f FILENAME] [-cf CAL_FILENAME] [-res RES] [-pc] [-ui] [-d]`

optional arguments:  
  ```
  -h, --help            show this help message and exit
  -f FILENAME, --file FILENAME
                        input (device, file, video, stream)
  -cf CAL_FILENAME, --calibration-file CAL_FILENAME
                        input for calibration (device, file, video, stream)
  -res RES              display resolution
  -pc                   for testing on pc
  -ui                   use user interface, assumes -pc      # currently not functional
  -d, --debug           show more debug output
  ```  
example run configurations:  
```  
billardtrainer.py -pc -res 1280x720
billardtrainer.py -pc -f http://192.168.0.59:8080/video -pc -d  
billardtrainer.py -f resources/20190405_172601.jpg -cf resources/experimental/20190405_172601.jpg -d -pc  
billardtrainer.py -f resources/20190405_172601.jpg -cf resources/experimental/cal_1.jpg,resources/experimental/cal_2.jpg,resources/experimental/cal_3.jpg -d -pc -res 800,450  
```
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

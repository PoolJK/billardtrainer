## Software in project

Usage: `python detect_test.py [-h] [-f FILENAME] [-d] [-ui] [-pc]`

optional arguments:  
  ```
  -h, --help                    show this help message and exit  
  -f FILENAME, --file FILENAME  image file to process  
  -d, --debug                   show more debug output  
  -pc                           for testing on pc  
  -ui                           use user interface, assumes -pc
  ```  
#### classes/
Platform-independent classes for the parts of the system under development.

#### raspy/
The script for development on the Raspberry-Pi.

#### resources/
Folder for all non-code files.

#### test_ui/
A script for development convenience, possibly extendable to actual UI
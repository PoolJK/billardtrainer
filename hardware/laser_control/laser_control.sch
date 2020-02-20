EESchema Schematic File Version 4
LIBS:laser_control-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 4
Title "Laser Control"
Date ""
Rev "1.0"
Comp "Jörg Krein"
Comment1 "© 2019"
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Sheet
S 3450 4700 1550 1050
U 5CF4E06E
F0 "Power" 50
F1 "power.sch" 50
$EndSheet
$Sheet
S 6000 2100 1500 1000
U 5CF4E0E7
F0 "DAC" 50
F1 "da.sch" 50
F2 "SCK" I L 6000 2650 50 
F3 "SDI" I L 6000 2550 50 
F4 "CS" I L 6000 2350 50 
F5 "LDAC#" I L 6000 2450 50 
$EndSheet
$Sheet
S 3500 2100 1500 1050
U 5CF4DFEE
F0 "USB-Connect" 50
F1 "usb_connect.sch" 50
F2 "SPI_CS" O R 5000 2350 50 
F3 "SPI_MOSI" O R 5000 2550 50 
F4 "SPI_CLK" O R 5000 2650 50 
F5 "LDAC#" O R 5000 2450 50 
$EndSheet
Wire Wire Line
	5000 2650 6000 2650
Wire Wire Line
	6000 2550 5000 2550
Wire Wire Line
	5000 2350 6000 2350
Wire Wire Line
	5000 2450 6000 2450
$EndSCHEMATC

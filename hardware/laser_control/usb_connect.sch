EESchema Schematic File Version 4
LIBS:laser_control-cache
EELAYER 29 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 4 4
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L power:GND #PWR026
U 1 1 5CF63425
P 4550 4900
F 0 "#PWR026" H 4550 4650 50  0001 C CNN
F 1 "GND" H 4555 4727 50  0000 C CNN
F 2 "" H 4550 4900 50  0001 C CNN
F 3 "" H 4550 4900 50  0001 C CNN
	1    4550 4900
	1    0    0    -1  
$EndComp
Wire Wire Line
	4550 4600 4550 4700
Wire Wire Line
	4550 4700 4650 4700
Wire Wire Line
	4650 4700 4650 4600
Connection ~ 4550 4700
Wire Wire Line
	4550 4700 4550 4900
Text HLabel 3600 4000 0    50   Output ~ 0
SPI_CS
Text HLabel 3600 4100 0    50   Output ~ 0
SPI_MOSI
Text HLabel 3600 4300 0    50   Output ~ 0
SPI_CLK
Wire Wire Line
	4050 4000 3750 4000
$Comp
L power:+5V #PWR025
U 1 1 5CF658DB
P 3750 3450
F 0 "#PWR025" H 3750 3300 50  0001 C CNN
F 1 "+5V" H 3765 3623 50  0000 C CNN
F 2 "" H 3750 3450 50  0001 C CNN
F 3 "" H 3750 3450 50  0001 C CNN
	1    3750 3450
	1    0    0    -1  
$EndComp
Wire Wire Line
	3750 3450 3750 3500
Wire Wire Line
	3750 3800 3750 4000
Connection ~ 3750 4000
Wire Wire Line
	3750 4000 3600 4000
Wire Wire Line
	4050 4100 3600 4100
Wire Wire Line
	4050 4300 3600 4300
$Comp
L Device:R R21
U 1 1 5D013E85
P 3750 3650
F 0 "R21" H 3820 3696 50  0000 L CNN
F 1 "10k" H 3820 3605 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 3680 3650 50  0001 C CNN
F 3 "~" H 3750 3650 50  0001 C CNN
	1    3750 3650
	1    0    0    -1  
$EndComp
$Comp
L Device:LED D1
U 1 1 5CFB53A8
P 3200 2600
F 0 "D1" V 3239 2483 50  0000 R CNN
F 1 "LED" V 3148 2483 50  0000 R CNN
F 2 "digikey-footprints:LED_3mm_Radial" H 3200 2600 50  0001 C CNN
F 3 "~" H 3200 2600 50  0001 C CNN
	1    3200 2600
	0    -1   -1   0   
$EndComp
$Comp
L Device:R R20
U 1 1 5CFB6919
P 3200 2950
F 0 "R20" H 3270 2996 50  0000 L CNN
F 1 "220R" H 3270 2905 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 3130 2950 50  0001 C CNN
F 3 "~" H 3200 2950 50  0001 C CNN
	1    3200 2950
	1    0    0    -1  
$EndComp
Wire Wire Line
	4050 3200 3200 3200
$Comp
L Connector_Generic:Conn_01x04 J4
U 1 1 5CFB85AB
P 5600 3700
F 0 "J4" H 5680 3692 50  0000 L CNN
F 1 "Conn_01x04" H 5680 3601 50  0000 L CNN
F 2 "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical" H 5600 3700 50  0001 C CNN
F 3 "~" H 5600 3700 50  0001 C CNN
	1    5600 3700
	1    0    0    -1  
$EndComp
Wire Wire Line
	5050 3600 5400 3600
Wire Wire Line
	5050 3700 5400 3700
Wire Wire Line
	5050 3800 5400 3800
Wire Wire Line
	5050 3900 5400 3900
Text Notes 3550 2450 0    79   ~ 0
Powers from USB
NoConn ~ 4050 3000
NoConn ~ 4050 3100
NoConn ~ 4050 3300
NoConn ~ 4050 3400
NoConn ~ 4050 3500
NoConn ~ 4050 3600
NoConn ~ 4050 3700
NoConn ~ 4050 3800
NoConn ~ 5050 3000
NoConn ~ 5050 3100
NoConn ~ 5050 3400
NoConn ~ 5050 4000
NoConn ~ 5050 4100
NoConn ~ 5050 4200
NoConn ~ 5050 4300
$Comp
L MCU_Module:Arduino_Nano_v3.x A1
U 1 1 5CF4E51C
P 4550 3600
F 0 "A1" H 4550 2511 50  0000 C CNN
F 1 "Arduino_Nano_v3.x" H 4100 2600 50  0000 C CNN
F 2 "Module:Arduino_Nano" H 4700 2650 50  0001 L CNN
F 3 "http://www.mouser.com/pdfdocs/Gravitech_Arduino_Nano3_0.pdf" H 4550 2600 50  0001 C CNN
	1    4550 3600
	1    0    0    -1  
$EndComp
NoConn ~ 4450 2600
NoConn ~ 4650 2600
Text Notes 5400 3400 0    79   ~ 0
for debugging
$Comp
L power:+5V #PWR030
U 1 1 5D012919
P 4750 2200
F 0 "#PWR030" H 4750 2050 50  0001 C CNN
F 1 "+5V" H 4765 2373 50  0000 C CNN
F 2 "" H 4750 2200 50  0001 C CNN
F 3 "" H 4750 2200 50  0001 C CNN
	1    4750 2200
	1    0    0    -1  
$EndComp
$Comp
L Device:R R26
U 1 1 5D013B66
P 4750 2400
F 0 "R26" H 4820 2446 50  0000 L CNN
F 1 "n.b." H 4820 2355 50  0000 L CNN
F 2 "Resistor_SMD:R_0805_2012Metric_Pad1.15x1.40mm_HandSolder" V 4680 2400 50  0001 C CNN
F 3 "~" H 4750 2400 50  0001 C CNN
	1    4750 2400
	1    0    0    -1  
$EndComp
Wire Wire Line
	4750 2200 4750 2250
Wire Wire Line
	4750 2550 4750 2600
NoConn ~ 4050 4200
Text HLabel 3600 3900 0    50   Output ~ 0
LDAC#
Wire Wire Line
	4050 3900 3600 3900
$Comp
L power:+5V #PWR0101
U 1 1 5D052F5B
P 3200 2200
F 0 "#PWR0101" H 3200 2050 50  0001 C CNN
F 1 "+5V" H 3215 2373 50  0000 C CNN
F 2 "" H 3200 2200 50  0001 C CNN
F 3 "" H 3200 2200 50  0001 C CNN
	1    3200 2200
	1    0    0    -1  
$EndComp
Wire Wire Line
	3200 2200 3200 2450
Wire Wire Line
	3200 2750 3200 2800
Wire Wire Line
	3200 3100 3200 3200
$EndSCHEMATC

EESchema Schematic File Version 2  date 9/17/2011 3:12:49 PM
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:special
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
EELAYER 43  0
EELAYER END
$Descr A4 11700 8267
encoding utf-8
Sheet 1 1
Title ""
Date "17 sep 2011"
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Text Notes 6925 5100 0    60   ~ 0
Integration board P2-4\nJumper wire to integration board P1-7\nIntegration board P1-6\nZ limit switch (normally closed)\nIntegration board P1-5\nIntegration board P1-4\nY limit switch (normally closed)\nIntegration board P1-3\nIntegration board P1-2\nX limit switch (normally closed)\nIntegration board P1-1\nIntegration board P3-7\n801-P3-7\nGND for 24V supply
Text Notes 8100 4300 0    60   ~ 0
Ongoing enabled latch circuit:\nK4 relay normally open -\nK1 relay normally open +\nK1 relay normally open -\n801-P3-4\nIntegration board P3-4\nIntegration board P2-4
Text Notes 6150 4300 0    60   ~ 0
Momentarily enabled servo reset path:\nK4 relay normally open -\n801-P3-5\nIntegration board P3-5\n7i37 OUT3+ (EMC2 servo reset signal)\nIsolated I/O MOSFET as switch\n7i37 OUT3-\nIntegration board P2-4
Text Notes 6925 3050 0    60   ~ 0
For K1 energize circuit:\n+24V\nK1 relay coil +\nK1 relay coil -\n801-P3-1\nIntegration board P3-1\nIntegration board P4-4\nEstop normally closed switch\nIntegration board P4-3\nIntegration board P3-8\n801-PC-8\nK4 relay normally open +\nthen in parallel:
Text Notes 1875 3725 0    60   ~ 0
For K4 energize circuit: \n+24V\nK4 relay coil +\nK4 relay coil -\n801-P3-6\nIntegration board  P3-6\n7i37 OUT1+ (EMC machine on signal)\nIsolated I/O MOSFET switch\n7i37 OUT1-\nIntegration board P3-7\n801-P3-7\nGND for 24V\n\n
Connection ~ 3450 1500
Wire Wire Line
	3450 650  4700 650 
Wire Wire Line
	3450 650  3450 3050
Wire Wire Line
	2900 550  2900 2250
Wire Wire Line
	2900 550  4700 550 
Connection ~ 4150 2250
Wire Wire Line
	2900 2250 4950 2250
Wire Wire Line
	4650 4425 4650 5100
Connection ~ 5050 5550
Wire Wire Line
	4800 5550 5050 5550
Wire Wire Line
	4000 5450 4000 5200
Wire Wire Line
	4000 5200 4950 5200
Wire Wire Line
	3000 1550 4700 1550
Wire Wire Line
	3000 1550 3000 2650
Wire Wire Line
	4700 1500 4700 1400
Connection ~ 3450 2450
Wire Wire Line
	4700 1500 3450 1500
Wire Wire Line
	4950 1950 3525 1950
Wire Wire Line
	4950 1950 4950 2050
Wire Wire Line
	4950 2050 3600 2050
Wire Wire Line
	3300 1950 1875 1950
Wire Wire Line
	3600 2050 3600 2350
Wire Wire Line
	3600 2350 4950 2350
Wire Wire Line
	4350 2950 3375 2950
Connection ~ 2225 1950
Wire Wire Line
	4550 2750 3300 2750
Wire Wire Line
	2225 2050 2775 2050
Wire Wire Line
	2775 2050 2775 2150
Wire Wire Line
	5950 7350 5950 4900
Wire Wire Line
	5950 4900 4850 4900
Wire Wire Line
	4850 4900 4850 4425
Wire Wire Line
	4800 6725 5050 6725
Wire Wire Line
	4850 4250 4850 2450
Wire Wire Line
	4650 4250 4650 2650
Wire Wire Line
	4450 4250 4450 2850
Wire Wire Line
	4800 6825 5700 6825
Wire Wire Line
	5700 6825 5700 5000
Wire Wire Line
	5700 5000 4450 5000
Wire Wire Line
	4450 5000 4450 4425
Connection ~ 3350 5950
Wire Wire Line
	3350 7350 3350 5000
Wire Wire Line
	3350 5000 4350 5000
Wire Wire Line
	3350 7125 4000 7125
Wire Wire Line
	4000 6050 3750 6050
Wire Wire Line
	3750 6050 3750 4900
Wire Wire Line
	3750 4900 4750 4900
Connection ~ 4250 4250
Wire Wire Line
	4250 4800 3650 4800
Wire Wire Line
	4250 4800 4250 3050
Wire Wire Line
	1875 1950 1875 2450
Wire Wire Line
	1875 2450 2775 2450
Connection ~ 2225 2550
Connection ~ 2225 2450
Wire Wire Line
	2775 2450 2775 2550
Wire Wire Line
	2775 2550 1875 2550
Connection ~ 2225 2950
Connection ~ 2225 2850
Wire Wire Line
	2775 2850 1875 2850
Wire Wire Line
	2775 2850 2775 2950
Wire Wire Line
	2775 2950 1875 2950
Wire Wire Line
	1875 2550 1875 2650
Wire Wire Line
	1875 2950 1875 3050
Wire Wire Line
	1875 2850 1875 2750
Wire Wire Line
	1875 2750 2775 2750
Wire Wire Line
	2775 2750 2775 2650
Wire Wire Line
	2775 2650 1875 2650
Connection ~ 2225 2650
Connection ~ 2225 2750
Wire Wire Line
	3650 4800 3650 7225
Wire Wire Line
	3650 7225 4000 7225
Wire Wire Line
	3350 5950 4000 5950
Connection ~ 3350 7125
Wire Wire Line
	4000 6925 3350 6925
Connection ~ 3350 6925
Wire Wire Line
	4350 5000 4350 2950
Connection ~ 4350 4250
Wire Wire Line
	4550 2750 4550 4250
Wire Wire Line
	4750 4900 4750 2550
Connection ~ 4750 4250
Wire Wire Line
	4950 2350 4950 4250
Wire Wire Line
	2225 2350 2775 2350
Wire Wire Line
	2775 2350 2775 2250
Wire Wire Line
	2775 2250 2225 2250
Wire Wire Line
	4850 2450 3450 2450
Connection ~ 2225 3050
Wire Wire Line
	2775 2150 2225 2150
Wire Wire Line
	4250 3050 3525 3050
Wire Wire Line
	3525 3050 3525 1950
Wire Wire Line
	4450 2850 3200 2850
Wire Wire Line
	3200 2850 3200 1200
Wire Wire Line
	3200 1200 4700 1200
Wire Wire Line
	1875 3050 3450 3050
Wire Wire Line
	4950 2250 4950 2150
Wire Wire Line
	4950 2150 3375 2150
Wire Wire Line
	4750 2550 3100 2550
Wire Wire Line
	3100 2550 3100 1400
Wire Wire Line
	3100 1400 4700 1400
Wire Wire Line
	4650 2650 3000 2650
Wire Wire Line
	4700 1550 4700 1650
Wire Wire Line
	4700 1650 3300 1650
Connection ~ 3300 1950
Wire Wire Line
	4950 5200 4950 4425
Wire Wire Line
	4650 5100 5050 5100
Wire Wire Line
	4550 4425 4550 5100
Wire Wire Line
	4000 6625 3850 6625
Wire Wire Line
	3850 6625 3850 5100
Wire Wire Line
	3850 5100 4550 5100
Wire Wire Line
	5050 5100 5050 6725
Wire Wire Line
	3300 2750 3300 800 
Connection ~ 3300 1650
Wire Wire Line
	4700 700  3375 700 
Wire Wire Line
	3375 700  3375 2950
Connection ~ 3375 2150
Wire Wire Line
	3300 800  4700 800 
Text Label 4700 800  0    60   ~ 0
IN3: ALL LIMITS OK
Text Label 4700 650  0    60   ~ 0
IN1: ESTOP OK
Text Label 4700 1650 0    60   ~ 0
OUT3: SERVO RESET
Text Label 4700 1500 0    60   ~ 0
OUT1: SERVO ENABLED
Text Label 4950 2250 0    60   ~ 0
ESTOP, NORMALY CLOSED
Text Label 4950 2050 0    60   ~ 0
ESTOP, NORMALY CLOSED
Text Label 4650 4150 1    60   ~ 0
+ SERVO RESET PATH -
Text Label 4850 4150 1    60   ~ 0
- GND for +24V DC +
Text Label 4950 4150 1    60   ~ 0
- ESTOP OK +
Text Label 4550 4150 1    60   ~ 0
+ SERVO ENABLED -
Text Label 4450 4150 1    60   ~ 0
+ SERVO OFF SIGNAL -
Text Label 4350 4150 1    60   ~ 0
+24V DC -
Text Label 4250 4150 1    60   ~ 0
+ K1 GND ENERGIZE -
Text Label 4750 4150 1    60   ~ 0
+ K4 GND ENERGIZE -
Text Label 4125 1200 0    60   ~ 0
SERVO OFF LED
Text Label 1600 2650 0    60   ~ 0
Z LIMIT N.C.
Text Label 1600 2850 0    60   ~ 0
Y LIMIT N.C.
Text Label 1600 3050 0    60   ~ 0
X LIMIT N.C.
$Comp
L GND #PWR?
U 1 1 4E73DE20
P 5950 7350
F 0 "#PWR?" H 5950 7350 30  0001 C CNN
F 1 "GND" H 5950 7280 30  0001 C CNN
	1    5950 7350
	1    0    0    -1  
$EndComp
$Comp
L +24V #PWR?
U 1 1 4E73D673
P 3350 7350
F 0 "#PWR?" H 3350 7300 20  0001 C CNN
F 1 "+24V" H 3350 7450 30  0000 C CNN
	1    3350 7350
	1    0    0    1   
$EndComp
$Comp
L CONN_8 P3
U 1 1 4E73D521
P 4600 4600
F 0 "P3" V 4550 4600 60  0000 C CNN
F 1 "801 PCB" V 4650 4600 60  0000 C CNN
	1    4600 4600
	0    -1   1    0   
$EndComp
$Comp
L CONN_6 P4
U 1 1 4E73D217
P 3800 2000
F 0 "P4" V 3750 2000 60  0000 C CNN
F 1 "CONN_6" V 3850 2000 60  0000 C CNN
	1    3800 2000
	-1   0    0    1   
$EndComp
$Comp
L CONN_6 P2
U 1 1 4E73D212
P 2575 2000
F 0 "P2" V 2525 2000 60  0000 C CNN
F 1 "CONN_6" V 2625 2000 60  0000 C CNN
	1    2575 2000
	1    0    0    1   
$EndComp
$Comp
L CONN_8 P3
U 1 1 4E73D1C2
P 3800 2700
F 0 "P3" V 3750 2700 60  0000 C CNN
F 1 "CONN_8" V 3850 2700 60  0000 C CNN
	1    3800 2700
	-1   0    0    1   
$EndComp
$Comp
L CONN_8 P1
U 1 1 4E73D1B4
P 2575 2700
F 0 "P1" V 2525 2700 60  0000 C CNN
F 1 "Integration Board" V 2625 2700 60  0000 C CNN
	1    2575 2700
	1    0    0    1   
$EndComp
$Comp
L RELAY_2RT K4
U 1 1 4E73D108
P 4400 5700
F 0 "K4" H 4350 6100 70  0000 C CNN
F 1 "MACHINE_ON" H 4550 5200 70  0000 C CNN
	1    4400 5700
	1    0    0    -1  
$EndComp
$Comp
L RELAY_2RT K1
U 1 1 4E73D103
P 4400 6875
F 0 "K1" H 4350 7275 70  0000 C CNN
F 1 "SERVO_ENABLE" H 4550 6375 70  0000 C CNN
	1    4400 6875
	1    0    0    -1  
$EndComp
$EndSCHEMATC

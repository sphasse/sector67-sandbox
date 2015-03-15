

# Introduction #
At the October 2011 monthly meeting at [Sector67](http://sector67.org), we went around and briefly introduced ourselves.  I mentioned I was working on the mill conversion, and John Lash from http://www.dancingarc.com (who makes some amazing kinetic art)
mentioned he was also working on a mill conversion.  After the meeting we continued discussing the conversions, and John graciously agreed to donate a set of three servo motors, encoders and servo controllers to the mill conversion effort.  As a direct result of that, the possibility of a servo-based 4th axis became a reality.

In addition, Scott attended the Nov 2011 [Madison SOUP](http://sundaysoup.org/madison-soup) event and with his presentation on the ProjectSheetCake 4th axis won the $180 kitty!  That prize money will go directly to fund a horizontal/vertical rotary table that we can convert to CNC control using a motor and controller from John.

This page provides more detail for our implementation of a fourth servo axis as part of the larger [Anilam EMC2 conversion project](ProjectSheetCake.md).

NOTE:  As of December 2011, work on the fourth axis capability this project has shifted to the FourthStepperAxis project.

# The hardware #
## The servo motor ##
The servo motors are Litton Clifton Precision brushed DC servos, U/T C23-L50W10M09, P/N 31-1200-0043, D/C 9547.  I have not been able to come by actual specs for these motors yet, but I have found a minimal amount of information here:

http://www.ni.com/devzone/advisors/motion/clifton.htm

Definition of symbols:
Tc	 = 	Continuous stall torque,
Ic	 = 	Continuous stall current,
Vr	 = 	Rated Voltage,
Tpk	 = 	Peak Torque,
Kt	 = 	Torque Constant,
Kv	 = 	Voltage Constant

|Model|Size|Max Tc (N-cm)|Max Ic (A)|Max Vr (V)|Tpk (N-cm)|Kt (N-cm/A)|Kv (V/krpm)|Vmax (V)|Max rpm (rpm)`*`|
|:----|:---|:------------|:---------|:---------|:---------|:----------|:----------|:-------|:---------------|
|C23-L50-W10|N23|29.7|5.7|  |254.2|5.2|5.41|  |5,549.1|

`*` Maximum Theoretical Speed at 48 V

and I am presuming that the servo controllers had been properly tuned for the servo motors, so I may be able to back into some specs from the controllers.

## The encoder ##
The motors came with an encoder already attached.  Pulling the tape covering one side of the encoder revealed the manufacturer and part number:

Computer Optical Products, Inc.
CP550-1000LD-4895

from the data sheet at:

http://www.opticalencoder.com/pdf/CP-500_size_15_hollow_shaft.pdf

this is a CP-550 Incremental Digital Hollow Shaft Encoder with 1000 cycles per revolution and linedriver pinout.  The pinout looking into the female 10 pin connector is:

|+5V|+5V|
|:--|:--|
|A |-A|
|B |-B| Notch |
|GND|I |
|GND|-I|

Since this is a linedriver output encoder with differential encoder signals, the default "TTL" encoder mode of the Mesa 7I33 will not work so we'll need to switch that axis to RS-422 mode and properly wire the inverted encoder signals from the encoder to the 7I33 board.  As the Anilam system used DB9 connectors for the encoders, we'll need to interface the 2x5-pin 0.1" header from the encoder to the DB9 connector on the integration board.


## The servo controller ##

The servo controller is a Copley Controls Corp model #412.  This is a 24-90VDC 10A DC brush servo controller card.  The data sheet can be found here:

http://www.copleycontrols.com/motion/pdf/412.pdf



# Interfacing to EMC2 #

## Modifying the integration board ##
The existing integration board wiring needed to be modified with extra connections to support the differential encoder mode, and one jumper on the Mesa servo interface board needed to be switched such that the A axis encoder can be read in differential mode.  After doing that the encoder was able to be read successfully in EMC2.

## Wiring the enclosure ##
# Making use of it #
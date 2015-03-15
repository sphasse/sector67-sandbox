

# Introduction #
This page contains documentation of the Anilam 1100M mill's HH Roberts spindle and SpindleBlok controller.  This is the spindle head for the Sector67 1100M mill that was [Converted to EMC2](ProjectSheetCake.md).  The HH Roberts spindle head was an aftermarket add-on to the Anilam mill to replace a failed head, and as such was basically not integrated into the mill controls except for the three-phase power contactors being enabled when the servos were enabled.

This generally worked fine as the mill does not have an automatic tool changer, and the manual controls ("local controls" in SpindleBlok terminology) provided sufficient feedback to run mill operations.

# Drive faulting #
However in mid-2011 the spindle started to have intermittent faults which put parts and tooling at risk because the mill would happily continue machining not knowing the spindle had stopped.  We started a somewhat lengthy diagnostic procedure that we hope will eventually lead us to a completely stable solution, with some of the steps being:

  * Review the wiring in the local control box.  Some of this is fairly shoddily done and could stand to be re-done but we don't believe this is currently the source of the faults.
  * Remove the VFD control panel cover to be able to view the flashing LED fault codes upon encountering a fault condition.  Viewing two faults in this way showed five flashes, which is a "DC Link Undervoltage" condition.
  * Enable the RS485 serial connection to the controller to be able to read system settings and older faults, and to be able to gather ongoing diagnostics and configure the drive as needed.  This is a small saga all by itself, and we had to work through several issues including:
    * Errant use of a null model cable instead of a straight through DB9 cable
    * Creation of a (subsequently unnecessary) custom headphone jack 12V power cable for the serial converter.
    * Mislabeled/confusingly labeled RS485 send/receive terminals
    * Unknown default serial port settings for the drive
    * Unknown device RS485 ID for the controller
> We were eventually able to work through all of these issues to achieve serial communication to the SpindleBlok controller.
  * Development of a Python-based RS485 serial terminal to simplify sending and receiving commands.  This software calculates the checksums of both send and received data and formats returned data into various forms.
  * Discovery and use of the SpindleWare Windows-based software for reading and writing data to the controller.  This software provides great diagnostic information and interprets the information from the controller for easy consumption.

Using SpindleWare, we are able to see that the last four fault conditions were:

TODO: capture this information here (All were DC Undervoltage)


The SpindleBlok manual describes these fault conditions as:

|Fault No (hex)|Fault No (decimal)|Fault LED|Blink Count|Description Cause and Remedy|
|:-------------|:-----------------|:--------|:----------|:---------------------------|
|3000h|12288|3 |Phase Overcurrent|The motor current sensors detected excessive current and shut the drive down. If this happened during commissioning or at start, the current regulators may be unstable. Try reducing the current regulator gains by half (parameters K07 kp\_i\_nom and K08 kd\_i\_nom). If this does not solve the problem, make sure that the motor parameters match the motor. Make sure the magnetizing current (G18 k\_id) is not too large. It should not be above 60 except in special cases. Try reducing the per-unit-resistance (G17 k\_rs) by half and recommissioning. If the overcurrent happened while the motor is loaded, try reducing the load limit (G10 load\_lim). If the motor rated current matches the drive rated current then the load limit should not exceed 200%. If the overcurrent happened during field weakening then check the slip limit (G11 slip\_lim). Most standard AC motors have a slip limit between 200% and 300%. Special spindle motors may have a limit as high as 450%. Also make sure that the appropriate rated slip is programmed by setting rated speed (G02 rated\_speed). If this is a low slip motor then you may need to reduce the rate limits on flux (L04 flux\_rate\_lim\_pos and L05 flux\_rate\_lim\_neg). Finally experiment with the leakage inductance parameter G06 ll\_lm by increasingor decreasing it by 10.|
|5000h|20480|5 |DC link undervoltage|The voltage sensor has detected a low bus voltage. If the drive is a 240 volt or 480 volt class drive with three phase power within line voltage specification then the most likely explanation is that a momentary input line dropout occurred. If the problem persists, monitor the input line voltage. If the input power is single phase or the drive is a 115 volt class drive then drawing excessive power from the motor may droop the line or cause enough ripple on the DC bus to cause an undervoltage trip. Increasing the DC bus capacitance will reduce the DC bus ripple.|


The !Spindleware software has a software oscilloscope facility that we can use to capture ongoing data.  Until we are able to resolve the fault condition completely, we are asking mill users to run the oscilloscope diagnostics during their milling operations.

Of course now that we have better diagnostic monitoring in place the controller has not faulted after many hours of operation.

# EMC2 integration #
The current plan is to integrate the drive to EMC2 in a few stages.  The first stage will be to tie the spindle fault condition into EMC2 such that when/if the controller faults, the mill will stop.

The second stage will be to configure EMC2 to monitor additional drive parameters such as RPM.

The third stage will be to configure EMC2 to optionally be able to control the spindle automatically, either via I/O lines or RS485 serial commands.  The drive unfortunately does not talk modbus, so there would be some customization work to get serial control fully working.

The sections below describe those stages.

## Integration stage 1: spindle controller fault ##
This was begun in early November 2011, with the basic steps being:
  1. Wire one of the digital output pins of the SpindleBlok to the isolated I/O card.
  1. Configure the SpindleBlok via the RS485 serial interface to send the appropriate output signal on the wired output pin
  1. Configure EMC2 via pncconf to treat the wired input pin as a spindle fault.

The plan was basically a good one, but several problems were encountered before it could be completed successfully:

  1. The way Anilam is setup to control the spindle, when the machine is not enabled, the 3-phase 240V power is not flowing to the spindle controller.  Since the spindle controller internal logic is also ultimately powered from this supply, the SpindleBlok as configured is not manageable via the serial console unless it is powered.  The relay board, on the other hand, only powers the SpindleBlok if it is in a non-estop state.  So, there is a basic chicken-and-egg problem both in configuring the SpindleBlok (which can be overcome to some degree), and more importantly on SpindleBlok startup.  More on this below.
  1. I had initially assumed the digital outputs were TTL logic, but in fact they are open collector outputs that need to be pulled up to an external voltage.  After using the on-board 12V supply through a 3k resistor, EMC2 was then able to see the state changes from the spindle controller.

The various documentation sources define polarity of their signals like so:

|Source|Name|Description|
|:-----|:---|:----------|
|SpindleBlok output|Fault xrst (Fault Assert)|Asserted when the drive is faulted, except when the fault is the reset fault. De-asserted when the fault is cleared.  When digital outputs are asserted, the digital output pins are pulled low.|
|Mesa 7i33 Isolated I/O card|Connector 4 pin 9|The opto-isolated inputs have 4.4K Ohm series resistors and reverse input protection diodes across the opto-isolator LEDS. Input current an the maximum 24V input is approximately 5mA. The isolated inputs will work with input voltages from 4 to 24V.  All controller interface pins are active low. This means a low controller output indicates power applied to an opto-isolated input. A low output activates the corresponding output MOSFET.|

So the fundamental problem with the start-up process and wiring is that in a powered-off state, there is no 12V source and the Mesa card will report a low (active) state.  When the 12V source is established, the line will be pulled up to a high state, and the Mesa card will report a high state, interpreted as a fault.  As configured during testing, this caused the power to be cut off to the spindle and EMC2 to be put in an estop state.

So, any attempt to get to the machine on state resulted in an immediate return to the estop state.

Even using the relay outputs with a voltage source from the mill would have this same problem, as the relay would also go through either an open->closed->open or closed->open->closed transition as the controller started up, although that can be verified.

We have implemented a solution that includes implementing a classicladder rung to delay enabling a spindle fault until some delay after the machine is enabled.  We named a custom input pin in pncconf for the servo-fault signal from the VFD and tied that to an estop ladder program implementing the enable delay.  The output of that ladder program was fed into the estop ladder rung as another source of estop.

Implementing this solution tool a little more work than expected, since the simple pncconf assignment of an estop signal to an input signal needed to be replaced with a custom classicladder program for estop.  The pncconf capability of specifying a custom estop program was used, and then that custom.clp was modified to add the servo reset ladder program needed to enable the servos (documented on the [main](ProjectSheetCake.md) page) and a separate spindle fault classic ladder program that required the machine to be on before considering the spindle fault an estop condition.  The spindle-fault classicladder program is shown below:

![http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/spindle-fault-ladder-program.png](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/spindle-fault-ladder-program.png)

The signals to integrate with this program were integrated via separate a hal file:

spindle-fault.hal:
```
#enable signal in from the machine
net enable => classicladder.0.in-15
#spindle fault in from the VFD
net spindle-fault => classicladder.0.in-16
#spindle fault out to the classicladder estop
net spindle-fault-out <= classicladder.0.out-15
net spindle-fault-out => classicladder.0.in-03
```

that is sourced from the custom\_postgui.hal file:

```
# Include your customized HAL commands here
source analog-joystick-jog.hal
source servo-reset.hal
# put a pound sign in front of the line below to disable spindle faults
# causing estops
source spindle-fault.hal
```

The classicladder.0.in-03 signal is an input to the estop rung.  The spindle fault was created in classicladder as a high signal representing a fault, so that if we really wanted to run without the spindle powered up, we can simply comment the sourcing of the spindle-fault.hal program in the custom\_postgui.hal file, that signal will be low, and will not generate an estop.

As of 2011/11/07 this solution has been tested and is now in production on the mill.


There is one more minor TODO which is to use an add-on component to generate a message that it was in fact the spindle that faulted.  Work has begun on this solution, using the message comp that is supposed to be bundled in version 2.5.  Since it is not bundled in our current version, the steps to install the component are:

  * Download the code of the comp from [this discussion thread](http://thread.gmane.org/gmane.linux.distributions.emc.user/29167) and save it to a file named "message.comp".
  * Run the following to install the comp:

```
sudo comp --install message.comp
```

The component should then be successfully built and installed.
  * Then the component can be loaded, specifying the appropriate configuration for a custom spindle fault message:

```
TODO: get the file from the current mill
```

TODO
## Integration stage 2: spindle RPM feedback and monitoring ##
This has not yet begun, but will involve either reading the RPM serially or reading an analog output pin into EMC2.  To read the analog output pin, we'll need to have an analog to frequency converter and configure an encoder in EMC2.

Looking at this problem further, it appears that integrating via a python user space HAL module to send serial commands to the VFD should be fairly straightforward.  The python implementation provided is current 2.6.5, and pySerial is installed.  A rough outline of tasks would be:

  1. Create a generic serial buffer python module configurable with baud rate, etc.
  1. Create a python module to send and receive the appropriate commands to the SpindleBlok, including checksum calculation and verification.  This is largely done.
  1. Create a script that exposes HAL pins for key metrics and forward/reverse/RPM
  1. Create a PyVCP panel to expose the spindle information
  1. Create a custom HAL module to hook the axis spindle pins up to the python module

All-in-all some work is required, but it would give nice flexible control of the spindle without needing to re-wire or disable the local controls or create voltage-to-frequency and frequency-to-voltage circuits for driving the RPM.  This approach would be user space only and thus not able to perform coordinated spindle motion, so that is probably the most significant drawback.

## Integration stage 3: spindle control ##
In the long run, once we no longer want the option to convert back to the Anilam controls, we could change the spindle wiring such that it was generally powered up but not enabled.  This would probably give us better failure modes (brake the spindle on an estop for instance rather than coast to a stop), and allow the serial communications to work even when the spindle was faulted.  However, there is perhaps something to be said for powering down the spindle completely.

If the VFD digital logic could be separately powered from an external source that would probably provide the best of all worlds, but I have not found an option for that in the SpindleBlok manual.


As a separate thought, it would be good to hook up external fault as well so that an estop will brake the motor.  This should also be fairly easy by feeding the 12V supply.  However, since the Anilam servo board is turning power to the spindle off on an estop, we still might not get the braking we want in an estop state.

Looking at this problem further, writing a python hal module that would perform the serial communication might be one relatively straightforward way of making this work.  More flexible and perhaps simpler than wiring it in local control mode and making an analog signal via PWM to drive the speed analog VFD input.  Too bad the VFD does not have a PWM input as that would be trivial.

# Useful links #
Some useful links for this spindle head are:

The HH Roberts manual for the complete head, including some basic wiring diagrams and diagnostic codes.  It is probably important to note that this spindle head no longer ships with a SpindleBlok, but a different VFD controller:
  * http://www.hhrobertsmachinery.com/HHRM-docs/Topwell/GL%20220V%20Head%20Replacment%20Manual%20Rev%204A.pdf

The SpindleBlok manual describing the VFD controller in detail:
  * http://www.compumotor.com/new_ulm/manuals_download.htm
  * http://www.compumotor.com/new_ulm/manual/Spindle.zip
  * http://www.compumotor.com/new_ulm/pdf/5004-0502%20layout%20asrd.pdf

The SpindkeBlok Windows serial control software.  Very helpful for configuring the controller and reading diagnostics.
  * http://www.compumotor.com/new_ulm/downloads_current.htm
  * http://www.compumotor.com/new_ulm/Downloads/SpindleWare_1p00p01_Release_10p29p2004.zip

Our own Python-based serial terminal that calculates checksums, sends commands, etc.:
  * http://code.google.com/p/sector67-sandbox/source/browse/#svn%2Ftrunk%2FRS485Terminal%2Fsrc

RS485 serial converter manuals:
  * [.md](.md)TODO
# Project Sheet Cake #
A three-axis CNC Mill Conversion from Anilam 1100M controls to EMC2

[![](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/board-pictures/mill-thumb.jpg)](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/board-pictures/mill.JPG)

_The mill mid-conversion_



## Introduction ##
In 2010, Sector67 (http://www.sector67.org) acquired two CNC mills, one with an Anilam 1100M control system and one with an Anilam 3300 control system.  At the time the CNC portion of the 3300 mill was non-functional but since then both of the mills have been brought into use and have generally been workhorses, with the 1100 mill being used primarily.  Although the Anilam 1100 system overall is somewhat dated, it has provided the needed functionality for many members to start down the path of CNC mastery.  We have worked to extend the existing system for our needs, writing a standalone Anilam post processor for converting abitrarily large gcode files in the most accurate way possible:

http://code.google.com/p/sector67-sandbox/wiki/AnilamPostProcessor

and a Python-based DNC program for running large programs via the serial port:

http://code.google.com/p/sector67-sandbox/wiki/AnilamPostProcessor

As we look to make best use of these mills in the hackerspace, we are hitting some of the limitations of the Anilam system.  In parallel other members have been developing our capability to perform 3D printing including building and tuning a couple of [CupCake](http://wiki.makerbot.com/cupcake) CNC and RepRap-based systems and working on plastic extrusion print head issues.  Debugging some of these print issues led to a discussion around print head stability, and the potential to use our CNC mills as a 3D printing platform.

The Anilam control system is unfortunately not well suited for extension to additional axis and arbitrary machine and motion control.  However, the servos, servo controllers, spindle and other portions of the mill are rock solid, which led us to think of converting the mill to make use of more modern hardware and software that could more easily be adapted to the various sorts of arbitary precision machine control needs that might come up at a hackerspace.  Specifically, of course, decorating a sheet cake.

So, in the spirit of the CupCake CNC, which is named for the approximate size of artifact it can create, we have dubbed our CNC mill conversion project "Project Sheet Cake".

## Choosing control hardware and software ##
When looking at possible choices for updated software and hardware, two software choices in particular were contenders.  [EMC2](http://linuxcnc.org/) and Mach3 both have large groups of adherents and active development work ongoing.  However, for control of our servo system, EMC2 makes more sense as Mach3, which runs as an application on top of Windows, is geared primarily toward bit-blasting stepper systems.  If we wanted to control the servos via Mach3, we'd need a hardware-based solution to manage the servo encoder feedback loop.  This tends to be more expensive hardware-wise.

EMC2, on the other hand, runs on top of Linux with a real-time kernel and can thus handle the encoder feedback in software on the PC.  In addition, EMC2 is open source software which in many ways better fits the hackerspace ethic.

With respect to the interface hardware, it is very common with both Mach3 and ECM2 to use a parallel port to drive no-feedback stepper systems.  However, with our drives we needed the ability to read digital encoder input from three axis and output analog +/-10V signals to drive the servo amplifiers.  A couple of folks had already done conversions of the scale we were considering using hardware from Mesa Electronics (http://mesanet.com).  Although they offer no discount to hackerspaces, support for their hardware in EMC2 is very mature, and their costs in any case are on the lower side of the servo-capable interface hardware.  The fact that their PCI cards are arbitrary I/O cards based on Xilinx FPGA will hopefully give us as much flexibility as we could want.

Specifically, we have chosen the following boards from [Mesa](http://mesanet.com):

  * A [5I23](http://mesanet.com/pdf/parallel/5i23man.pdf) FPGA based PCI  Anything I/O card.  This card will go in the PC, and 50 pin ribbon cables will provide signals to the daughter cards.  Currently $229 in small quantities.

  * A [7i33TA](http://mesanet.com/pdf/motion/7i33man.pdf) quad analog servo interface daughter card.  This card will be wired to provide the servo amps with the appropriate +/-10V input signals, and take the encoder signals in and clean them up for EMC2.  Currently $79 in small quantities.

  * A [7i37TA](http://mesanet.com/pdf/parallel/7i37man.pdf) isolated I/O daughter card.  This card will be used to provide isolated output from EMC2 for the servo enable and servo reset signals (amongst other things), and to provide input of some machine state to EMC2.  Currently $79 in small quantities.

## Basic architecture ##
This diagram shows the basic high-level architecture of the system:

![http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/basic-architecture.png](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/basic-architecture.png)

_The original svg source for this image is under revision control in the sector 67 sandbox source repository._

# Understanding the new interface components #

## The integration board ##
The integration board is a custom-made board designed to hold the Mesa daughter boards for interfacing with the existing mill's 0.2" and DB9 plugs providing power, estop, limit, rotary encoder in and servo amp out in the servo amp box. It is designed to be a plug and play replacement for the Anilam S1100 distribution board in the large chassis that holds the servo amps.

We've taken great pains to design this board such that if we ever wanted to restore the original Anilam functionality, that could easily be done.

The base of this board is a piece of (TODO: get gauge) 7"x12" aluminum sheet, with a 1/2" strip along the 12" edge folded at 90 degrees to give stiffness and provide a way to secure the board to the chassis.

On top of this sheet we've attached the Mesa daughter boards, serial connectors and through hole prototype perf boards for securing the connector headers and other components with 3/8" standoffs.

The right hand side of this board primarily handles servo drive I/O, with the encoder input coming from the drives on the DB9 connectors with the signals as described in the encoder section below.

There were several special considerations when designing and implementing this board.

  * Since we wanted to make the board plug-compatible with the existing mill, we needed to source 0.2" two-layer header connectors.  The appropriate headers are listed in the parts list
  * Most serial connectors are designed as through-hold board components or cable ends.  In addition, prototype breakout boards for serial connectors are somewhat hard to come by.  So, in order to be able to attach the serial connectors securely to the aluminum sheet, we used female DB9 ribbon connectors and used standoffs to attach the DB9 connectors directly to the board.  We then stripped and tinned the individual wires from the ribbon cable so that they could be directly terminated in the screw terminals of the 7i33TA servo controller card.
  * Some of the standoffs were in electrical contact with the solder traces on the perf board, so a plastics standoff were used.  In the next iteration of this project, I would use a slightly bigger perf board to avoid this problem.
  * There are some electrical considerations for this board.  Servo amps can be electrically noisy, and so signals should be shielded where possible.  We should also avoid ground loops (http://en.wikipedia.org/wiki/Ground_loop_%28electricity%29) and make sure things are generally grounded appropriately.  We should make sure the PC is on the same AC supply as the servo amps and other power supplies, to avoid ground differentials across the 50 pin ribbon cables.  One good source of documentation for considerations in machine control environments is http://www.pmccorp.com/support/manuals/emc.pdf.
  * When EMC2 exits, the 5i23 watchdog puts all pins into a high-impedance state.  The board should be designed to kill power in this state, and active low outputs should be used to enable functionality.  This is why you will see controller output used as a ground drains.

A schematic of the integration board is shown below:

![http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/integration-board-schematic.png](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/integration-board-schematic.png)


The full board schematic file suitable for editing with [KiCad](http://www.lis.inpg.fr/realise_au_lis/kicad/) is under revision control and is available in the [S67 code sandbox](http://code.google.com/p/sector67-sandbox/source/browse/#svn%2Ftrunk%2FProjectSheetCake%2Fschematics).  The image above was generated from that schematic using KiCad.
TODO: finish parts list, pictures, component layout and schematic.


Integration board parts list
| **Part** | **Price per** | **Quantity** | **Description** | **Vendor** | **Part Number** |
|:---------|:--------------|:-------------|:----------------|:-----------|:----------------|
| 2x8 0.2" terminal plug | $4.85 | 2 | A through-hole soldered terminal plug with two rows of 8 pins. | Digikey | A98151-ND |
| 2x6 0.2" terminal plug | $3.65 | 5| A through-hole soldered terminal plug with two rows of 6 pins. | Digikey | A98150-ND |
| DB9 female ribbon connector | $5.67 | 4 | A female DB9 plug with ribbon cable connector | Digikey | AFR09B-ND |
| 3/8" Standoffs  | $0.72 | 40 | 3/8" male/female #4-40 brass standoffs for attaching the daughter boards and perf boards to the aluminum sheet | Digikey | 7200K-ND |
| 1/4" Standoffs | $0.653 | 10 | 1/4" male/female #4-40 standoffs for attaching the DB9 connectors to the 3/8" standoffs | Digikey | 8713K-ND |
| #4-40 screws | $0.0298 | 40 | #4-40 screws for connecting the boards to the standoffs | Digikey | H342-ND |
| #4-40 nuts | $0.0093 | 40 | #4-40 nuts for connecting the standoffs to the aluminum sheet   | Digikey | H216-ND |
| 9-wire ribbon cable | N/A | 4 | 9-wire 0.05" pitch ribbon cable for the DB9 plugs.  Approximately 10" long for the longest run.  I split 9-wire ribbons off of a salvaged floppy disk cable | N/A | N/A |
| Connecting wire | N/A | ~5' | Various lengths and colors of 22 gauge stranded wire for connecting the through-hole perf board components to the daughter boards and for connecting parts on the perf board.  I used wire salvaged from cables.  | N/A | N/A |
| 2"x4" Prototype perf board | $6.26 | 4 | 0.1" hole spacing prototype perf board with copper on one side. | Digikey | V2025-ND |
| Red LEDs | $0.48 | 10 | Red light-emitting diodes for on-board indicators | Digikey | 511-1256-1-ND |
| Green LEDs | $0.52 | 10 | Green light-emitting diodes for on-board indicators | Digikey | 511-1254-1-ND |
| 2.2k 1/2 watt LED pull-up resistors | $0.093 | 20 | Pull-up resistors for LEDs on the 24V circuits | Digikey | 2.2KH-ND |

A picture of the completed integration board is shown below.

[![](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/board-pictures/whole-board-thumb.jpg)](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/board-pictures/whole-board.JPG)

_More pictures of the integration board can be found at [S67 code sandbox](http://code.google.com/p/sector67-sandbox/source/browse/#svn%2Ftrunk%2FProjectSheetCake%2Fdocs%2Fimages%2Fboard-pictures)_

There are 9 LEDs on the integration board, and from left to right, when lit they represent:

| **Position** | **LED name** | **Meaning** |
|:-------------|:-------------|:------------|
|1 |24V OK|The integration board is getting +24V from the relay board|
|2 |X LIMIT OK|The X axis limit switches are not being tripped.|
|3 |Y LIMIT OK|The X nor Y axes limit switches are being tripped|
|4 |Z LIMIT OK|The X nor Y nor Z axes limit switches are being tripped|
|5 |A LIMIT OK|The X nor Y nor Z nor A axes limit switches are being tripped|
|6 |ALL LIMITS OK|None of the limit switches are being tripped|
|7 |ESTOP OK|The estop button is not being pressed|
|8 |SERVO ENABLED|EMC2 is sending a signal that the servos should be enabled.  The servo reset still needs to happen for the servos to actually get power.|
|9 |SERVO OFF (red)|The servos are not enabled.  The servo amplifiers should not be receiving power.|

Of these, only ESTOP OK (inverted) and ALL LIMITS OK (not inverted) are being sent into EMC2 as input signals.  Since the limit switches are in series, you have to look at the first unlit LED to determine which axis is at limit.  For instance, if the X axis is at limit, X, Y, Z and ALL LIMITS will be unlit.  If the Y axis is at limit, the X axis will be lit, but Z and all will be unlit.  The A axis limit is not hooked up, and there is a jumper skipping it currently.

## The PCI I/O card ##
The PCI I/O card was fairly easy to install.  It installs as a typical full-height PCI card, and the ribbon cables are run out the back in a slot left open for this purpose in the end of the card.  The card has jumper-settable supply voltage for the daughter cards, which should already be set at +5V.  The other voltage settings were already at +3.3V, so out of the box this card was configured correctly for my purposes.

After installing EMC2 via the live CD, I verified that the hostmot2 packages were already installed, so there was no additional work there, and looking through dmesg output, the board was identified by the driver without issue.

Because of the way the hostmot2 driver and pncconf work, we are running the servo functions off of the #1 50 pin ribbon, any potential stepgen functions off of the #2 50 pin ribbon, and custom isolated I/O off of the #3 50 pin ribbon.  The reason for this is that the hostmot2 driver is not compatible in its stepgen pin assignments with the isolated I/O card for stepgens, so we'd run any stepper drivers with TTL logic.  Whereas the limit, enable out, etc. need to be isolated I/O.

This is not really a limitation for us, as we currently have plenty of isolated I/O from just one 7i37TA daughter card.

## The 50 pin ribbon connectors ##
I originally ordered 1' 50-pin ribbon connectors from Mesa, but realized quickly these would be much too short for this application.  Luckily, we had some longer 50 pin cables sitting around S67.  Old SCSI cables with any terminators removed seem to work fine for testing purposes at least.

Once we get things fully working, I want to find the distance from the PC to the daughter cards and get/make appropriate twisted pair ribbon cables:

| **Part** | **Price per** | **Quantity** | **Description** | **Vendor** | **Part Number** |
|:---------|:--------------|:-------------|:----------------|:-----------|:----------------|
| CABLE 50 COND 5FT TWISTED PAIR | $18.20 | 3 | 5' 50 conductor 0.05" pitch twisted pair ribbon cable for the card connections | Digikey | MC50F-5-ND |
| 50 pin cable ends | $2.86 | 6 | CONN SOCKET 50POS W/ STRAIN RLF | Digikey |OR987-ND |

TODO: finish this once we settle on where the PC will live relative to the controller.

Twisted pair cables are somewhat better in that they reduce the exposure to RF interference.  The cables should be shielded between the PC and the controller box.

# Understanding the current mill and controller #
## The servo encoders ##
Since servo motors, unlike steppers, are not able to be directly controlled to move a specific distance via input only, some feedback is necessary in order to be able to accurately position them.  Our servo motors have two types of feedback, an analog velocity, which is fed back to the servo amplifiers directly, and a incremental (quatrature) rotary encoder.  The rotary encoder is read by EMC2 and used to accurately determine how far the motors have moved.  There are several types of rotary encoders, and ours, as is typical on servo motors, are incremental rotary encoders.  You can learn more about these at the following links:

http://en.wikipedia.org/wiki/Rotary_encoder#Incremental_rotary_encoder

http://prototalk.net/forums/showthread.php?t=78

But the basic idea is that there are two encoder signals, A and B, which are enabled 90 degrees out of phase from one another.  These signals pulse high and low as the shaft is rotated, and so accurate sensing and counting of the pulses relative to one another allows you to keep track of how far the shaft has turned and in which direction.  There is a third encoder signal, X, which pulses high once per full rotation of the shaft.  In addition to these three signals, the encoders on our motors require +5V and a ground, so there are a total of 5 wires for each servo motor: A, B, X, +5V, GND.  These wires come from the servo motor into the round connector in the case (documented elsewhere) and from there into a DB9 connector with the pin out documented in the integration board schematic.

The 7i33 can be configured via jumpers for two sorts of encoder input, TTL or RS-422 ("differential").  The encoder signal on our motors are 0V to +5V TTL, so the 7i33 jumpers were left in the default TTL configuration.  The alternative (RS-422) uses both positive and negative voltage and is good for sending signals longer distances.  We take the TTL encoder signals and wire them to the The 7i33 servo controller daughter board, which cleans them up for the PCI card and ultimately EMC2. The 7i33 daughter board also provides ground and +5V to the encoders.

While the encoder feedback primarily allows for accurate positioning, it does have an additional benefit that the controller can determine when the machine is not accurately following the instructions given.  This sort of error is called "following error" and when EMC2 detects following error it will put the machine into an machine stopped but non-estop state.

While the encoders provide information about the shaft turning, they do not specify an absolute linear distance moved by a given axis.  In order for EMC2 to be able to accurately position the system, it needs to be able to translate rotary encoder pulses into a linear distance moved.  This depends on both the pitch of the mill lead screws and the number of pulses per turn of the encoders.  A procedure for determining those is described in the [Basic Machine Parameters](#Basic_machine_parameters.md) section below.

Direct linear encoders are also sometimes used.  These measure the movement of the table itself via pulses, but our mill does not have them.  Linear encoders are helpful in that you can directly measure and compensate for backlash in lead screws, but they are tend to be more complex and are not cheap.

## The servo enable/estop circuit ##

The current Anilam server enable circuit is basically a set of four relays that are used to provide 120VAC to the servo power supply and power to the spindle relay.  Most of the heavy lifting of the servo enable circuit is done on a separate circuit board ("Anilam PC 801") that contains the physical relays and connects to out integration board via an 8 pin header.  If you are working on servo enable problems or want to understand how the servos are enabled, you should read this section.

Although it would be possible to run the estop and limit functions completely in software with emc2, we are choosing to preserve the existing hardware solution, with machine state being read by emc2.

Since our mill does not have separate limit/home switches, this effectively means that we will not be able automatically home to a machine absolute zero.  However, since nearly all of our milling is currently done relative to a local zero this will hopefully not be a severe limit.  With so many different users using the mill, and potentially even working on the emc2 software, a hardware hard limit seemed like the more prudent decision.  Separate home switches could be added in the future if that feature is needed.

Each axis has a set of limit switches that are wired in series, along with an DPST (double pole single throw) estop button.  These switches are all normally closed, and provide part of the 24V ground circuit for the bottom two (as viewed in the box) relays on the relay board.

The relays are:

K4: **Top relay**, enabled state represents servo enable,
Ground path controlled by the PC "servo enable" flag.
When energized helps complete the ground path for K1 and K3.

K1: **Middle relay**, active output facilitates the latching circuit by providing the ground circuit to itself
Ground path controlled by (in series):

  * The limit switches
  * The estop button
  * The K1 relay being energized and/or the SERVO\_RESET path enabled.
  * The K4 relay being energized

When energized, helps completes the ground path for K1 and K3
The closed when non-energized portion of this relay controlls the "servo off" signal to the PC.

SERVO\_RESET is meant to be temporarily engergized to allow the latch state to be set up.  It should then be disabled so that if the ground path is broken via the limit switches, estop, etc., K1 will be de-energized.

K3: **Bottom relay**
Ground path is the same as K1
When energized drives the K2 solid state relay on the back side of the board to enable the spindle relay and provide 120VAC to the servo amp power supply.

The signals from the integration board to the Anilam PC 801 board are shown below, pin 1 being the lower right pin on the integration board:

|Integration board pin|Relay board pin|Description|
|:--------------------|:--------------|:----------|
|P3-1|1 |K1, K3 ground side of the relay coils.  On the integration board, this is fed to the normally closed estop button.|
|P3-2|2 |+24VDC supply from the relay board|
|P3-3|3 |Signal pin indicating the servos are in an off state.  This is connected to the normally closed output of the K1 relay.  It is either +24V (servos off) or open (servos on)|
|P3-4|4 |Connects to the K1 relay normally open output, and is a part of the estop/limit ground path.  On the integration board, this pin is wired to the ALL\_LIMITS\_OK pin.|
|P3-5|5 |Connects between the K1 relay normally open output and the K4 relay normally open output.  On the integration board, this pin is connected to the ALL\_LIMITS\_OK pin through the SERVO\_RESET EMC2 output.  Momentarily enabling SERVO\_RESET provides a temporary path to ground for the K1 coil (bypassing the K1 output), so that the K1 relay gets to a latch state where it is providing its own ground signal.|
|P3-6|6 |Connects to the ground side of the K4 relay.  On the integration board, this is connected to ground through the EMC2 MACHINE\_ON signal.|
|P3-7|7 |GND for the +24V supply|
|P3-8|8 |Connects to the normally open output of the K4 relay.  On the integration board, this is connected to the normally-closed estop switch.|

![http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/servo-reset-circuit.png](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/servo-reset-circuit.png)

_A logical view of the servo reset circuit.  The fill circuit diagram in KiCad format is available for download in the S67 sandbox_
## The servo amplifiers ##
The existing servo amplifiers are Anilam brand amps.  TODO: Anilam part number here.  We don't have ready specs on the amps, but since they work with the existing controller, they seem to be serviceable.  They take in +/-10V for direction and speed, and they receive velocity feedback from the motors.

Via testing, we determined that a positive voltage moves the table in a positive direction for all of the axis, but it could have just as well have been the reversed.  There are three wires coming from the integration board for each amp, a signal, a ground and a shield.  The 7i33 card is set up to take in direction and pulses and convert that to output +/-10V, so it is basically ideal for us to drive the existing servo amps.

You can see from the integration board schematic how the servo amplifiers are hooked to the 7i33 servo control board.

# EMC2 #

## Choosing and validating a PC ##
Because EMC2 runs using a real time Linux kernel, it has specific hardware requirements.  Most notably, the system needs to be able to respond to low-level requests in a specific (low) amount of time in order for EMC2 to be able to perform critical motion-control hardware functions such as counting encoder pulses and stepping stepper motors.

Because of this, functions such as power-saving and on-board graphics tend to not work well on real-time systems.  EMC2 provides a latency-test tool that can be used to evaluate your system to see if is acceptable for use as an EMC2 system:

http://wiki.linuxcnc.org/emcinfo.pl?Latency-Test

Our EMC2 server machine specs are:

```
Compaq W6000
Bios and version: TODO: get
Memory: TODO: get
Video card: TODO: get
etc.
```

When running this against the default configuration of our candidate PC, the max jitter numbers where over 8,000,000, which would render it unusable for EMC2.  After reviewing the EMC2 documentation on jitter, we reconfigured the BIOS settings for power management (BIOS -> Power -> Energy Saver -> Mode = Disabled) and (BIOS -> Power -> Energy Saver -> Fan Speed = High ).  I'm not sure that the fan speed setting was strictly necessary, so this should be tested, as in a machine shop environment running the fan only when needed would keep things cleaner.

After changing those settings, we saw much better jitter numbers:

|Max Interval (1.0 ms thread)|Max Jitter(ns) 1.0 ms thread|Max Interval (25 us thread)|Max Jitter (25 us thread)|
|:---------------------------|:---------------------------|:--------------------------|:------------------------|
| TODO: document | 6,799 | TODO: document | 19,099 |

Which basically means this server will be fine for EMC2, both in servo and stepper mode.


## Installing EMC2 ##
EMC2 is fairly easy to install.  We burned a copy of the live cd:

http://linuxcnc.org/index.php?option=com_content&task=view&id=21&Itemid=4&lang=en

configured the PC's BIOS to boot from the CD first, rebooted and chose the installation option.  There were a few simple choices to be made, the most notable of which were the locale, host name, user name and password, and we chose to have the user automatically logged on at startup.

After the installation process finished successfully, we removed the live CD, reconfigured the BIOS to boot from the hard drive, and restarted to a functional Ubuntu system with EMC2 installed.  This was an astonishingly simple alternative to what I thought might be quite daunting (getting the real-time kernel extensions working, etc.).

After install, there were options to start EMC2, view the documentation or run of several utilities.

One minor Linux customization was to configure the screen saver not to lock the PC, and to have it only come on after 30 minutes.

## Updating EMC2 ##
Since there are many fixes available to the live CD version of EMC2 (2.4.3), updating is recommended.  We initially did not do this and as a result a bug in pncconf caused us to lose a significant amount of time.  The updated procedure can be found at:

http://buildbot.linuxcnc.org/

We are using Lucid (Ubuntu 10.4) 32-bit only (not the simulation), and chose to update to the 2.4 branch.  The documented update procedure took around 10 minutes to download and install the components.  No problems have been encountered so far due to updating to the latest stable version.

## Configuring EMC2 ##
Once EMC2 was installed, we started it via Applications -> CNC -> EMC2.  It prompted for a configuration, and we chose "hm2-server -> 5i23" as that matched our configuration.

From there, basically no additional work was needed to have things basically work.  The 7i23, server control daughterboard was hooked up to the first of three 50 pin outputs from the 5i23, and after confirming this is where the configuration expected it by viewing the pinouts via dmesg, we hooked up the encoders and they worked properly the first time.

After that, we hooked up the Z-axis servo amp and it also worked the first time, with intermittent following errors.  EMC2 was basically functional for moving servos and reading encoders out of the box with the appropriate example configuration.  VERY NICE!

## Tuning EMC2 ##
Reading through all of the various resources, this can be somewhat of a dark art, but there are some basic things that can be done to make this go smoothly.  We had to work through a problem with runaway axes that was ultimately a bug in pncconf.  To realize that, though, we had to take a methodical approach to tuning the system that ultimately was good practice and exposure to some of the internals of EMC2.  This section describes that tuning procedure.

### Basic machine parameters ###
You'll need to know some basic things about your machine to configure EMC2 properly.  For servo systems, to determine how far the table moves per encoder pulse, you'll want to know:

  * The number of teeth per inch on your lead screws
  * The number of encoder pluses per motor revolution
  * The ratio of gear teeth on the motor gear the lead screw gear

To determine the teeth per inch on the lead screws, you can inspect the screw directly with a caliper, or put a dial indicator on the table and turn the handles to measure an inch.  Again, this should turn out to be a fairly round number.  Ours was 5.

You can determine the combination of the number of pulses per motor revolution and gear ratio by running pncconf, getting to the axis configuration and running the open loop servo test ("open loop" means that the PID feedback loop is not in place, so the servos will not be completely stable).  To determine the encoder pulses, you should run this without power applied to the servos.  Simply turn the handles one full revolution and watch the encoder pulses in the appropriate halmeter window.  It should end up being a nice round number, but if there is any doubt, you could for instance give it 10 turns and divide by 10.  The number you get from this will be the number of rising and falling edges, and since there are two encoder signals both rising and falling, you divide this number by 4 to get encoder pulses per revolution.  For our mill, we saw 6000 edges per revolution, so our number was 1500.  If you leave the gear ration set to 1:1, you can use this number.  If you'd rather find the actual gear tooth ratio, you'll have to open up covers and count, and then adjust the encoder pulses appropriately to account for the gear tooth ratio.

If you are converting an Anilam mill like us, there is a simpler way to get this information.  In the Anilam interface, on startup navigate to TODO document path, and you should see a table with the exact information you need.  In our case, that was:

|              | **X** | **Y** | **Z** |
|:-------------|:------|:------|:------|
| **Enc Lines**  | 1000 | 1000 | 1000 |
| **Pitch**      | 0.2  | 0.2  | 0.2  |
| **Ratio**      | 1.5  | 1.5  | 1.8  |

"Enc lines" is the encoder pulses per revolution of the motor, "pitch" is the lead screw pitch (0.2 = 5 TPI) and "ratio" is the gear ratio of motor teeth to lead screw teeth.  In the pncconf calculator you should enter a gear ratio that matches this.  In our case, 2:3 (3/2 = 1.5) would be appropriate for the X and Y axes and 5:9 (9/5 = 1.8) would be appropriate for the Z axis.

Once you have this information, enter it into the fields in pncconf in the per-axis "Calculate" form that let you calculate the Axis Scale.  An example of this looks like:

![http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/axis-scale-calc.png](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/axis-scale-calc.png)

This needs to be done for each axis.  On our mill, the values are:

|              | **X** | **Y** | **Z** |
|:-------------|:------|:------|:------|
| **Pulley teeth motor**  | 3 | 3 | 9 |
| **Pulley teeth leadscrew**  | 2 | 2 | 5 |
| **Encoder lines per revolution** | 1000  | 1000  | 1000  |
| **Leadscrew TPI**      | 5.0  | 5.0  | 5.0  |
| **Calculated scale**   | 30,000 | 30,000 | 36,000 |

Of course every machine is different.  I did confirm these measurements after putting them in EMC2 by putting a dial caliper on each axis.

### Max velocity and acceleration ###
TODO: find a way to determine this

### Calibrating the encoders ###
There are two important dimensions to proper encoders.  They should indicate movement in the proper direction, and they should accurately indicate the distance moved.

Before you start applying power to the servos, you'll want to make sure your encoders are configured properly.  Again using the open loop servo test in pncconf without servo power applied, manually move the axis under test.  When you move it in a positive direction, you should see this reflected in pncconf positively.  The same for negative.

It is probably important to note that for most systems, an X+ move will be moving the table to the left, and an X- move will be moving the table to the right.  A Y+ move will move the table forward, and a Y- move will move the table back.  A Z- move will move down and a Z+ move will move up.  This can be somewhat counter-intuitive with an empty bed, but think as if you are machining a part and you should be OK.

If your encoders are not the right direction (ours all were), you can either re-wire the A and B wires, or switch the configuration in software.

If you have entered the appropriate scaling information, you can also confirm at this time that the encoders reflect an accurate amount of movement.

### Initial motor calibration ###
Once you have the encoders calibrated, you can then perform the initial calibration of the servo motors.  Once again, the pncconf open loop servo tester can be used.  In that tool, click the servo enable button.  In our case, since we had an extra "servo reset" to establish a hardware relay latch, I additionally detached the header that provides servo enable and reset and shorted the servo enable pins.  I then could momentarily short the servo reset pins to actually enable the servos.  This is one downside of the non-standard "servo reset" signal.  Obviously, you'll need to be careful if shorting pins to perform the "servo reset".

Th first thing you should determine is if the system moves in the + direction when clicking the + button.  If not, you'll need to check the TODO: get checkbox name check box to reverse the signal in software, and then clicking the + button should move the axis in the + direction.

TODO: a screen shot of the X axis configuration page.

### Motor PID fine-tuning ###
Reading through all of the available resources show that this is somewhat of a dark art.  There are a few basic methodologies described well [here](http://en.wikipedia.org/wiki/PID_controller#Loop_tuning).  In any case it is good to document as you work through the process, like so:

|Axis|P|I|D|Result|
|:---|:|:|:|:-----|
|X |1 |0 |0 |Slow to stop|
|X |2 |0 |0 |Still slow to stop|
|X |5 |0 |0 |Still slow to stop|
|X |10|0 |0 |Getting better|
|X |15|0 |0 |Basically stable operation|
|X |15|0 |0 |Axis oscillation (1/2")|
|X |9 |4.5|1.125|Rapid axis oscillation (~1/8")|
|X |9 |4.5|0 |Basically stable, seemingly not as good as 15 0 0|

**NOTE**: these are example values gathered when the axes were not scaled properly.

TODO: document how we ultimately tuned in the mill.

# Extending the system #
One of the major goals of this retrofit was to enable additional system customizations and extensions.  This section describes some of those customizations and extensions.

## Automated servo reset pulse ##
### Introduction and considerations ###
The Anilam mill had a separate servo reset button that was used to establish a hardware relay latch circuit as part of the estop/limit servo enable circuit.  As mentioned above, as different people might be hacking on the EMC2 software, we wanted to maintain hardware-level estop, limits, etc.  This meant preserving the Anilam servo enable/relay board, and the servo reset signal as well.  Since the Axis EMC2 interface does not have a concept of servo reset, it needs to be added as custom functionality.

There are several ways of doing this, including:

  * Map a different output signal.  My initial quick and dirty implementation of mapping it to the spindle clockwise output signals.  This was not ideal as the spindle cw signal is not momentary, and I once left it enabled and hit a limit switch.  Since the limit switches were not yet hooked into EMC2 properly, movement stopped but EMC2 did not get out of the machine on state, and so when I manually moved the machine back in limit, the servos activated and ran the machine out of limits again.  So, having it possible for the servo reset signal out to not be momentary is not safe.  It was a quick and dirty method to make progress in other directions though.
  * Adding a custom Axis PyVCP GUI push button.  David is working on using PyVCP to integrate a servo reset button into the AXIS GUI.  This is indefinitely on hold as the automated pulse generation described below has worked fine.
  * Automatically generate a pulse.  It is possible to have EMC2 generate a ~1s servo reset pulse automatically upon going to the machine on state.  This is a good use case for a custom classicladder program.  This is the approach we ended up implementing, and this section describes that implementation.

In a nutshell, ladder logic is a programming language that uses relays and other physical objects as a programming metaphor.  Ladders of logic are programmed, a classicladder hal component is loaded and associated with the servo thread, a specific classic ladder program is loaded and mapped into a namespace, and the inputs and outputs of that are mapped to HAL pins so that the program can affect changes in EMC2.

A momentary output pulse based on going to the machine on state is a very simple ladder program, but provides a good demonstration of how this sort of customization is done.  An excellent classic ladder tutorial can be found in the EMC2 Integrator's Manual.

### Creation of the ladder program ###
After enabling the classic ladder component in pncconf, when you start EMC2 you will have a "File->Ladder Editor" option to start the ladder editor.  The ladder editor is a bit clunky, but the EMC2 integration manual is somewhat helpful.  Pncconf expects your custom program to be stored in the same directory as the rest of the configuration and named custom.clp.  If in our case you need a custom estop as well, when you choose that in pncconf it automatically adds entries into the hal files to load the classic ladder module, integrate the estop ladder program and load your custom.clp program.

The ladder program for the one-off servo-reset pulse looks like so:

![http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/servo-reset-ladder-program.png](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/servo-reset-ladder-program.png)

There is a simple input, an IEC timer in TP mode with a 2 second preset and a simple output.  Documentation of all of the classic ladder components can be found here:

http://linuxcnc.org/docs/html/ladder_classic_ladder.html

and the custom.clp program itself is available from the S67 code sandbox.  The custom.clp currently includes three rungs:

  * A custom estop program that includes the spindle fault as an estop source
  * The servo reset functionality on machine on
  * The spindle fault functionality to ignore spindle faults until one second after the machine in in the on state.

### Integration using pncconf ###
Pncconf provides a standard way to integrate existing custom ladder programs into your configuration.  You enable it to do so by choosing (TODO: names of the check box) to enable ladder logic and TODO: custom estop option.  You also need to select (TODO: get name) so that it will add entries to the ini file to load the custom\_postgui.hal file by default.  The custom\_postgui.hal file contains additional hal commands to source files that associate the classicladder pins with pins and signals that actually do something in EMC2.  Pncconf will generate a custom\_postgui.hal file for you once, but will then not overwrite it.  In our case, we wanted to read the input from the "enable" signal as %I10 in our ladder program, so we need a line in custom\_postgui.hal like so:

```
net enable => classicladder.0.in-10
```

I chose to assign the a custom-named digital output via pncconf to be "servo-reset".  This allows me to assign the classicladder %Q10 output pin to the servo-reset signal with the following lines in custom\_postgui.hal:

```
net servo-reset <= classicladder.0.out-10
```

You can assign custom names to input and output pins in pncconf simply by selecting the pin and typing the name.

### Verification of the functionality ###
After making those changes, you will need to restart the axis interface, and you should be able to go into the classicladder editor and confirm the pin assignments by pushing the "signals" button.  It should have actual assignments like this:

TODO: signals image

You should then be able to visually confirm operation of the ladder program by enabling the machine and watching the a one second pulse signals flow through the ladder editor GUI.  The servos should actually enable of course as well.

In addition, you can use halmeter (launched from the Axis GUI menu) to watch the servo-reset net to (hopefully) observe the correct behavior.

## The spindle ##
This implementation is described at [1100SpindleBlok](1100SpindleBlok.md).
## Generic relays and solenoids ##
## Additional steppers ##
## A fourth servo axis ##
This implementation is described at [FourthServoAxis](FourthServoAxis.md).
## Custom keyboard mappings ##
We want the space bar to pause a running program.  Custom keyboard mappings can be implemented for the axis interface by putting the appropriate commands into the ~/.axisrc file as documented here:

http://linuxcnc.org/docs/html/gui_axis.html#r1_11_4

The proper ~/.axisrc file commands to map the space bar to program pause and display this on the help page are:

```
root_window.bind("<space>", "task_pause")
help2.append(("Space", "Pause program"))
```

These values were determined by looking at the possible keyboard bindings within tkInter and the tasks in axis.tcl.  More keyboard bindings are definitely possible as needed.

TODO: put this in place for real.

TODO: implement a dead man switch on the joystick jog so that if the joystick gets accidentally activated somehow it is not a danger.

# Lessons learned so far #
  * EMC2 is a lot more mature, stable and user-friendly than I expected.  There are some important concepts to understand, but it really is a great system.

  * The pin numbers shown in pncconf may different than the pin numbers on the isolated I/O board, which might be different than the pins on the 50 conductor ribbon cable.  You need to use the isolated I/O board manual to make sure you map these pins correctly.

  * pncconf is a great time saver, but it is not bug free and sometimes does things that are not expected.  It helps to understand a bit about what it is doing by looking at the generated .hal and .ini files.

  * You should update to the latest stable EMC2, in case there are bug fixes that apply to your situation.

  * The hostmot2 driver maps specific pins to PWMGens, encoders and stepgens, so moving the isolated I/O to the third 50 conductor cable helped keep the hard-coded isolated I/O out of the way of more flexible motor control scenarios.

  * All circuits should be designed such that losing power disables them, and that the default initial and post-watchdog state of the 5i23 board do not cause bad behavior.  This takes some planning.

  * Hardware estop and limits are a good thing to have.  In case of tuning issues or unexpected software or configuration problems, you always have a safe backstop.

# Additional changes #
6/13/2012, we've continued to work on this mill, taking out the extraneous Anilam components and installing things in a more permanent way.  The manual/auto spindle switch was re-integrated in a more generic way, which required wiring a jumper across the auto/manual switch input on the Anilam relay board.

All-in-all this retrofit continues to be a success.

# Build log #
Check out the SheetCakeBuildLog.

# TODO #
There are quite a few tasks remaining to complete this project.  Some of them are:

  * Video the existing Anilam components functioning properly so we can take them out and sell them (done)
  * Remove the unneeded boards and package and label them (done)
  * Move the PC to the left cabinet
  * Make 3x shielded 50-pin cables with the shielded cat 5 and 50-pin ends (done)
  * Wire the PC to the mill 120V inside the cabinet
  * Configure the PC bios to start upon receiving power, so that turning the mill on will boot the PC
  * Add a separate signal (non-power) conduit from the VFD to the right cabinet for estop signals and eventually potentially encoder and software control of the VFD.
  * Mount the stepper controller and power supply inside the right cabinet.  Consider potentially mounting these inside the left cabinet where we will have more space.  Access to estopped 120V power might be more difficult though. (done but on the 3300 mill)
  * Wire the 36V power supply to estopped 120V power (done but on the 3300 mill)
  * Mount the monitor holder on the monitor arm
  * get and mount a keyboard/mouse holder on the monitor arm
  * mount the separate estop button in an accessible location (done)
  * consider how to wire up an encoder for controlling feed override.
  * Complete the PID/FF tuning and configure following error to be realistic and helpful, vs. something like 1 inch which it is now.



  * 
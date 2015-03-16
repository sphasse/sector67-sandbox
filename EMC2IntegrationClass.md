# Implementing CNC motion control with EMC2 #
If you have a working mill or are planning to build one and are interested in controlling it via computer.  This class will prepare attendees to convert or build the computer control system for a mill or other machine with the Linux-based open source EMC2 software suite.  The class will cover choosing and configuring the software, PC, I/O interface components, electronic interface hardware, motors and motor controllers needed to move a machine.  The actual mechanics of machine building (axes, lead screws, etc.) are not covered in this class.



# Introduction to machine control concepts #
## Big picture goals ##
There are many different reasons for wanting to implement computerized motion control, including mills, lathes, plastic extrusion, plasma or laser cutting and other applications unrelated to manufacturing.  In all of these cases, we want to be able to move machines accurately, efficiently and reliably with the minimum hardware and software cost required to get the job done.  EMC2 as part of an overall motion control solution can help fulfill those goals.

## Brief gcode primer ##
To illustrate some of the challenges of motion control, we'll consider an extremely simple snippet of gcode to rapidly move the machine to the home position and then move one unit in the X direction at a feed speed of 100 units per minute:

```
G00 X0 Y0 Z0
G01 X1 Y0 Z0 F100
```

## Mass, momentum, acceleration and velocity ##
Assuming the machine is already at the home position, in an ideal world the machine would immediately start to travel at the feed rate, reach the end of the move and immediately stop.  In the real world of course, the table, motors and other moving machine components have mass and momentum and so the machine needs to accelerate to reach the desired velocity, and then decelerate to not overshoot at the end of motion.  Because of these real-world concerns, even seemingly simple machine motion operations present quite sophisticated motion planning challenges.

As a result, high-end motion control systems have historically incorporated relatively expensive dedicated motion planning hardware.  As the capabilities of general-purpose commodity PC hardware long ago surpassed what is needed for motion planning, it has become possible to use a PC instead of dedicated motion planning hardware, with one important caveat.  The software controlling the hardware must be capable of controlling the motors and (in the case of closed-loop control systems) reading motion feedback in "real time", or with a certain level of response time guaranteed.

Most modern operating systems are shared, interrupt-driven and function with ever-increasing abstraction away from physical hardware and cannot guarantee low response time needed for real-time operations.  However, there are several commercial real-time operating systems, and most important for EMC2, at least two options for real-time extensions to the Linux kernel that allow it to provide real-time capability.  EMC in particular makes use of the RTAI extensions, and these will be covered a bit more later.

## Understanding types of motors, feedback and encoders ##

Stepper and servo systems compare and contrast
### Stepper motors and controllers ###
An excellent introduction to stepper motors can be found [here](http://en.wikipedia.org/wiki/Stepper_motor).  Stepper motors turn a specific amount when a pulse is applied to a stepper motor controller.  Stepper motors typically have the most torque when stationary.  They are typically run in open loop control systems, and thus it is generally desirable to over-engineer them for a specific application as the open loop control system cannot compensate for lost steps.
### Servo motors ###

  * PID tuning concepts introduced

TODO: explain the torque differences between servos and steppers

## Simplified block diagram of a typical motion control system ##

![http://raw.githubusercontent.com/sphasse/sector67-sandbox/master/ProjectSheetCake/docs/images/motion-control-block-diagram.png](http://raw.githubusercontent.com/sphasse/sector67-sandbox/master/ProjectSheetCake/docs/images/motion-control-block-diagram.png)

  * User interface
  * Programmable motion controller
  * Interface hardware
  * Power supply
  * Motor controllers/amplifiers
  * Motors
  * Encoders
  * Encoder feedback

## Machine shop tour ##
Time to put see the simplified block diagram in practice in a few different configurations.  A tour of the Sector 67 machine shop will allow us to see at least three different types of systems that we can map onto our basic block diagram.

TODO: get pictures and post them

### Proprietary Anilam control system ###
The Anilam 3300 system is a sophisticated 3-axis closed-loop commercial servo system.  The user interface runs under DOS on a dedicated "PC on a card" industrial PC system.  The programmable motion control board is an ISA card.  Both of these are in the upper cabinet.  The interface hardware, which for this system also controls estop and limit functions and can completely disable servo amp power, is in the lower cabinet, along with the servo amplifiers and amplifier power supply.

### EMC2 converted control system ###
Many more details of our EMC2 converted system can be found at [ProjectSheetCake](ProjectSheetCake.md).  The User interface and programmable motion controller are EMC2 on a Linux real-time kernel.  The interface hardware is a Mesa PCI I/O board with daughterboards for servo control (cleaning up encoder input and performing frequency to voltage conversion for the servo control signals) and optically isolated I/O.  The Anilam estop and limit functions were preserved and are interfaced to EMC2 via isolated I/O.

### Small mill stepper control system ###
Joe's mini mill is an open-loop stepper control system using Mach3 on a Windows PC to control stepper amps.  This system performs motion planning in software and uses the PC's parallel port for interfacing to the Xylotex stepper motor controllers.

### Router table stepper control system ###
Scott's router table is also an open-loop stepper control system but using EMC2 to control stepper amps.

### A Makerbot ###
The Makerbot is an open-loop stepper-based system.  It uses a PC for the user interface, and an Arduino for the programmable motion controller.  GCode commands are sent to the Arduino via a serial interface, and the relatively low-power Arduino performs linear interpolation of any arc commands sent.


# Introduction to EMC2 #
## Introduction ##
EMC stands for "Enhanced Machine Control".  It is a software system for computer control of machine tools such as milling machines and lathes.  EMC is free software with open source code. Current versions of EMC are entirely licensed under the GNU General Public License and Lesser GNU General Public License (GPL and LGPL).  It is a very mature motion control platform, capable of control of up to 9 axes.

## Background and history ##
EMC was originally developed by the National Institutes of Standards and Technology as part of an effort to prove out the use of commodity hardware make manufacturing more efficient.  The open source community took the concept forward and implemented EMC2.

## EMC2 core concepts ##
The design of EMC2 makes it basically analogous to a component-based hardware system.  This is a useful for machine integrators, as what is typically a software "black box" control system is actually quite componentized and you can diagnose problems at the component level.  This also makes for a very flexible system as you can connect components in different ways for different functions.

The section below is basically copied from http://linuxcnc.org/docview/2.5/html/hal/intro.html#_hal_concepts_a_id_sec_hal_concepts_a.  It contains descriptions of key concepts needed to understand EMC2 configuration.

### Component ###
When we talked about hardware design, we referred to the individual pieces as "parts", "building blocks", "black boxes", etc. The HAL equivalent is a "component" or "HAL component".  A HAL component is a piece of software with well-defined inputs (pins and parameters), and outputs (also pins and parameters) that can be interconnected to other components via signals, and behavior (functions) that can be installed and run via association to a thread.

### Parameter ###
Many hardware components have adjustments that are not connected to any other components but still need to be accessed. For example, servo amps often have trim pots to allow for tuning adjustments, and test points where a meter or scope can be attached to view the tuning results. HAL components also can have such items, which are referred to as "parameters". There are two types of parameters: Input parameters are equivalent to trim pots - they are values that can be adjusted by the user, and remain fixed once they are set. Output parameters cannot be adjusted by the user - they are equivalent to test points that allow internal signals to be monitored.  HAL parameters are set via the "setp" command, and shown by the "show param" command.

### Pin ###
Hardware components have terminals which are used to interconnect them. The HAL equivalent is a "pin" or "HAL pin". ("HAL pin" is used when needed to avoid confusion.) All HAL pins are named, and the pin names are used when interconnecting them. HAL pins are software entities that exist only inside the computer.

### Signal ###
In a physical machine, the terminals of real hardware components are interconnected by wires. The HAL equivalent of a wire is a "signal" or "HAL signal". HAL signals connect HAL pins together as required by the machine builder. HAL signals can be disconnected and reconnected at will (even while the machine is running).  HAL signals are created and connected to pins with the "net" command.

### Function ###
Real hardware components tend to act immediately on their inputs. For example, if the input voltage to a servo amp changes, the output also changes automatically. However software components cannot act "automatically". Each component has specific code that must be executed to do whatever that component is supposed to do. In some cases, that code simply runs as part of the component. However in most cases, especially in realtime components, the code must run in a specific sequence and at specific intervals. For example, inputs should be read before calculations are performed on the input data, and outputs should not be written until the calculations are done. In these cases, the code is made available to the system in the form of one or more "functions". Each function is a block of code that performs a specific action. The system integrator can use "threads" to schedule a series of functions to be executed in a particular order and at specific time intervals.

### Thread ###
A "thread" is a list of functions that runs at specific intervals as part of a realtime task. When a thread is first created, it has a specific time interval (period), but no functions. Functions can be added to the thread, and will be executed in order every time the thread runs.

## Additional concepts ##

### NML ###
NML stands for Neutral Manufacturing Language.  It is the protocol used for communication between user interfaces and HAL.

### Type ###
When using real hardware, you would not connect a 24 volt relay output to the +/-10V analog input of a servo amp. HAL pins have the same restrictions, which are based upon their type. Both pins and signals have types, and signals can only be connected to pins of the same type. Currently there are 4 types, as follows:

  * bit - a single TRUE/FALSE or ON/OFF value
  * float - a 64 bit floating point value, with approximately 53 bits of resolution and over 1000 bits of dynamic range.
  * u32 - a 32 bit unsigned integer, legal values are 0 to 4,294,967,295
  * s32 - a 32 bit signed integer, legal values are -2,147,483,647 to +2,147,483,647

### Physical\_Pin ###
Many I/O devices have real physical pins or terminals that connect to external hardware, for example the pins of a parallel port connector. To avoid confusion, these are referred to as "physical pins". These are the things that "stick out" into the real world.

## Community and support ##
EMC2 has a thriving community and excellent support is available from several sources.  There is an IRC channel, emc-users (and developer) mailing lists, and online forums available .

## Basic architecture ##
TODO: paste diagram here

## Real-time considerations ##

### Base thread ###

### Servo thread ###
  * Comparison with Mach3
  * Choosing and testing PC hardware for EMC2
  * Choosing interface hardware for EMC2
    * Parallel ports
    * Dedicated I/O boards
  * The EMC2 live CD
  * Updating the software via the EMC2 buildbot
  * Running EMC2 in simulation mode for development and testing

## Exercise 1: installing a virtual EMC2 instance ##
The first exercise is to create a virtual EMC2 sandbox for yourself.  This sandbox will have multiple uses, including familiarizing yourself with EMC2 configuration, practice using various EMC2 GUIs, practice configuration editing and things like classic ladder development.

Please reference [InstallEMC2InAVirtualBox](InstallEMC2InAVirtualBox.md) for the detailed exercise.

# EMC2 configuration #
  * Keeping your software configuration under revision control
  * Using pncconf for generating your configuration
  * The HAL files
  * Hardware drivers
  * The ini file
  * User interface components
  * Axis UI

## HAL manual configuration exercise ##
Please work through the exercises in [the EMC2 2.5 documentation](http://linuxcnc.org/docview/2.5/html/hal/tutorial.html).

### Debugging EMC2 ###
  * HAL meter
  * HAL scope
  * HAL command lines

## stepconf configuration exercise ##

## pncconf configuration exercise ##


# Concerns when interfacing the hardware electronics #
  * Failure modes
  * Mains isolation
  * Electrical noise
  * Ground loops
  * Optical isolation
  * Physical robustness
  * Heat dissipation
  * Emergency stops
  * Machine limits

# Integrating the hardware electronics #
  * Review of the 1100 mill conversion integration


# Moving the machine under feedback control #
  * PID tuning applied

# Customizing EMC2 software futher #
## Introduction ##
LinuxCNC is an extremely versatile and open platform.  There are many possible paths for extension, some of which are covered here.

## Classicladder-based programs ##
Ladder programming is a type of programming model that uses relay contacts and coils and as a metaphor for program logic.  It is a common programming model in programmable logic controls (PLC's) and as such is familiar to some machine integrators.

More information can be found here:

http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Classicladder_Ver_7.100

http://www.linuxcnc.org/docview/2.5/html/ladder/ladder_intro.html

## PyVCP UI elements ##
You can integrate additional functionality into the Axis GUI via PyVCP panels.  The PyVCP elements are tied to HAL pis.  This is useful for instance for spindle control and information, as well as completely custom accessory integration.

http://www.linuxcnc.org/docview/2.5/html/hal/pyvcp_examples.html

## Custom gcode integration ##
LinuxCNC supports calling out to shell scripts via the user-defined M GCode words.  To use this facility, you create and name a shell script in the PROGRAM\_PREFIX directory and then call it using the M appropriate M code

http://www.linuxcnc.org/docview/2.5/html/gcode/m-code.html#_m100_to_m199_user_defined_commands_a_id_sec_m100_to_m199_a

You can pass parameters to the script via the P and Q words.

## Interfacing with HAL via command line ##
You can execute hal commands using the halcmd command line script.  This allows flexible integration for reading and writing pin values.  An example would be:

```
#!/bin/sh
# file to turn on parport pin 14 to open the collet closer
halcmd setp parport.0.pin-14-out True
exit 0
```

This can work in conjunction with user-defined M codes to iterface with custom hardware (e.g. M101 turns a relay on)

## Standard digitial and analog inputs and outputs ##
LinuxCNC has four standard digital inputs, four standard digital outputs, four standard analog inputs and four standard analog outputs.  The M62/63/64/65/66/67/68 gcodes control reading and writing these standard values.  They can be written immediately or synchronized with motion, depending on the gcode used.

## Command-line gcode ##
LinuxCNC comes with a shell interface called linuxcncrsh.  Using this interface you can send gcode commands using a remote program such as telnet.

http://www.linuxcnc.org/docview/2.5/html/man/man1/linuxcncrsh.1.html

## Displaying custom messages in axis ##
It is sometimes helpful to be able to display a custom message in the user interface.  In the 2.5 release there will be a built-in component to accomplish this, but currently doing this requires installing a custom component.

## Python conmponents ##
You can create LinuxCNC components using Python.  There is a simple API to export pins, parameters, etc. needed for your component.

You can then use the full power of python for things like talking over a serial port, image recognition, USB, etc.

Python components are userspace only.

## C components ##
C components can be userspace or real time.  There is a simplified C interface for creating components.

## Customized kinematics ##

http://www.linuxcnc.org/docview/2.5/html/motion/kinematics.html

EMC2 is used to control a wide variety of motion, including machines like hexapods

# Cool software extension examples #
## EMC2-based repstrap ##

https://github.com/brendanjerwin/emcrepstrap

This is a cool collection of extensions to LinuxCNC that basically allow an "off-the-shelf" makerbot printing head to be controlled from LinuxCNC.

# Customizing the hardware further #
  * Various 4th axis configuration scenarios
  * Probe input for touch off and automated sensing
  * Automated tool changers
  * Coordinated spindle moves (tapping, etc.)
  * Different spindle heads (plastic extrusion, frosting extrusion, tangential knife, etc.)
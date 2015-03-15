# Introduction #
Around August 2012 Sector67 began an effort to integrate a Huanyang 3HP VFP inverter HY02D223B(TODO: confirm the model #) to control the spindle on our formerly Anilam 1100 CNC mill.  The need for this transition was caused by the ongoing malfunctioning of our SpindleBlok/CapBlok VFD.  That device was faulting with a low DC bus voltage, even though the bus voltage itself seems to have been fine when measured externally.  This page describes some details of the Huanyang integration.


**NOTE: We currently do not recommend using this VFD.  The one supplied to us had terminals for a braking resistor, documentation implying a braking resistor would be used and configuration parameters for configuring braking resistor percentages.  However, after configuring appropriate parameters for a braking resistor the VFD went into an DC bus overvoltage condition and was subsequently.  Subsequent disassembly showed that the BRAKING RESISTOR TERMINALS WENT TO THE PC BOARD BUT NOWHERE FROM THERE.  Be strongly cautioned that this drive might not be what is advertised.**

We have subsequently switched to a Delta VFD, documented at [DeltaVFD](DeltaVFD.md).

The documentation is being left below for historical purposes.

# Basic approach #
There were several possible strategies for integrating the spindle control with the overall LinuxCNC-based system, including
  * Use analog output from the MESA cards and encoder input, along with the analog input functions of the VFD to implement full control of the spindle via LinuxCNC.  This would ultimately be interesting and allow rigid tapping, but as we have little need for that and typically tweak the spindle speed by hand (and sometimes run the mill in completely manual mode) we did not choose this path.
  * Use of the "Digital Operator" front panel on the VFD.  This could be extended to the front of the machine.  The interface is a bit clunky for newcomers however and is not very rugged, so we did not pursue this approach either.
  * Integration to LinuxCNC via RS485.  This would require some software tweaking but would be simpler than implementing a full control loop.  Again though the desire to use the spindle in manual mode precluded this path.
  * Use of the existing rugged analog control panel.  This panel has a potentimeter for RPM adjustment, an enable switch, a forward/reverse switch and a digital RPM display.  It also has a relay for latching estop functions.

We chose the existing analog control panel approach as it provided the most rugged interface that could be manually controlled.  This might be revisited in the future, especially integrating an encoder with LinuxCNC to provide accurate RPM.  We added to this approach improved integration into LinuxCNC, with a spindle fault sent to LinuxCNC and the LinuxCNC estop sent to the VFD.

# Issues #
We encountered several issues with the VFD, many of which have to do with the poor quality of the documentation.
  * The screw terminals on the VFP are fairly small for the expected current.  We had to grind down the sides of 10 gauge crimp terminal ends to be able to fit them into the terminals on the device.
  * The terminal labeled +5V seems to be high impedence and does not supply +5V.  This causes a re-work of the enable latching circuit because the existing relay was rated for 5v.  Luckily Chris had 24V CPDT relays handy.  The +5V is not documented on some of the diagrams in the manual, but is clearly labeld on the terminals, so this is a bit of a mystery.  I have not been able to find a setting that would "enable" the +5V output.  The corresponding 24V output works as expected.
  * An external fault is not forwarded to the fault output, making it very difficult to have the spindle lock register as a spindle fault.
  * The forward/reverse switch did not function as expected.  It had four terminals and three positions (forward, stop, reverse).  I had assumed this switch was single pole double throw and would have one pair open in the forward position and one pair closed, reversing that for the reverse position and both pairs open in the off position.  It turns out it had both pairs open in the off position, one pair closed in the reverse position and both pairs closed in the forward position.  There was no obvious way to make this switch scheme compatible with the input the VFD expected, so we had to switch to a different forward/off/reverse switch.  Chris had a switch in stock that worked as expected (Sector67 is amazing!).
  * Use of the braking resistor is not well documented and we still do not have it working fully properly.
  * The external fault reporting to LinuxCNC is not working properly currently.  We can simluate a fault by setting the deceleration time to 0.5 seconds and stopping the drive.

# Details #

A table of changed settings
(this table is neither complete not correct currently)
| Settings | Factory | Set to | Meaning |
|:---------|:--------|:-------|:--------|
| PD001    | 0       | 1      | Source of run commands is external terminal |
| PD002    | 0       | 1      | Operating frequencies controlled via external terminals |
| PD015    | 20.0    | 5.0    | Deceleration time #1 |
| PD030    | 0.0     | 5.0    | DC braking time at stop |
| PD031    | 2.0     | ?      | Increase slowly if braking does not stop the device. |
| PD026    | 0       | 0      | Decelerating stop (needed for braking) |
| PD028    | 0.5     | ?      | Stopping frequency.  Increase to apply braking sooner, not intended for deceleration, stopped braking only |
| PD044    | 02      | 02     | Configure input #1 (FOR) forward |
| PD045    | 03      | 03     | Configure input #2 (REV) forward |
| PD047    | 07      | 13     | Configure input #4 (SPH) as an external estop |
| PD048    | 19      | 13     | Configure input #5 (SPM) as an external estop |
| PD049    | 20      | 01     | Configure input #6 (SPL) as run enable (actually the drive does not function properly with run enable configured) |
| PD051    | 03      | 03     | Confirm Y2 output is fault indication.|

# References #
A wiring diagram for the HH Roberts analog control panel can be found here:

http://www.hhrobertsmachinery.com/HHRM-docs/Topwell/GL%20220V%20Head%20Replacment%20Manual%20Rev%204A.pdf

or

http://www.hhrobertsmachinery.com/Support/Manual_machine_Parts_Lists/Yaskawa/GL%20Yaskawa.JPG

The manual for the VFD can be found here:

http://www.cnczone.com/forums/attachment.php?attachmentid=79285&d=1239132143

# Wires from the control head #

|Wire  | VFD Side       |Control head side         | Meaning  |
|:-----|:---------------|:-------------------------|:---------|
|Gray  | Sindle lock    |                          |          |
|Purple| REV            | Direction switch reverse |          |
|Orange| FOR            | Direction switch forward |          |
|Brown | ACM            | Ground of speed POT and digital tach | Analog ground signal |
|Tan   | 10V            | Top of speed POT | +10V reference for speed control |
|Pink  | V0             | + signal of digital tach | Analog speed out |
|Red   | +24V           |                    | +24V for latch circuit |
|Black | VI             | Wiper of speed POT || Analog speed signal in|
|Blue  | No Connection  | latched ground     | Intended to be a run enable signal |

# Wires from spindle lock #

Spindle lock is normally closed, open when the spindle is locked
| Wire | Use |
|:-----|:----|
| Red | Gray signal wire to complete ground circuit. | Allows the spindle lock switch to be a part of estop |
| Black | DCM |  Digital ground signal |

# Wires from the Mesa card #
|Wire | Meaning |
|:----|:--------|
| Orange       | + of the digital input      |  Provides input to LinuxCNC when the spindle is faulted |
| Orange/white | Ground of the digital input |  |
| Blue         | + of the isolated digital estop out | Provides output from LinuxCNC when the system is estopped |
| Blue/white   | Ground of the digital estop out     |  |


# TODO #
TODO:
**Test the 5V output and see if it is enabled when the input is 5V.** Integrate the spindle lock as an external estop
**Integrate the LinuxCNC estop as an external estop (parallel)** Integrate the fault out into LinuxCNC
**Re-crimp the fan and re-lable it properly as 220V**

# Thoughts on this project #
In retrospect, it would have probably been easier to mount a cabinet on the back of the mill and mounted the VFD in that.  That would have meant re-wiring the three phases to the motor, the braking resistor, the control signals, and the 3-phase input (basically, re-wiring everything with longer wires).  However, that would have made future maintenance of both the VFD and mill head simpler.

However, for expedience we re-mounted the VFD in the same tight enclosure.  It barely fits and takes contortions to get everything mounted, but it is just workable.
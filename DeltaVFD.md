# Introduction #

After a bad experience with a Huanyang VFD, we subsequently integrated a Delta (TODO: get model) VFD.  The integration was fairly straightforward as the two VFDs were very similar.


# Details #

# Wiring details #
## Wires from the control head ##

|Wire  | VFD Side       |Control head side         | Meaning  |
|:-----|:---------------|:-------------------------|:---------|
|Gray  | Sindle lock    |                          |          |
|Purple| REV            | Direction switch reverse |          |
|Orange| FOR            | Direction switch forward |          |
|Brown | ACM            | Ground of speed POT and digital tach | Analog ground signal |
|Tan   | 10V            | Top of speed POT | +10V reference for speed control |
|Pink  | V0             | + signal of digital tach | Analog speed output to the digital tach|
|Red   | +24V           |                    | +24V for latch circuit |
|Black | VI             | Wiper of speed POT | Analog speed signal in |
|Blue  | No Connection  | latched ground     | Intended to be a run enable signal |

## Wires from spindle lock ##

Spindle lock is normally closed, open when the spindle is locked
| Wire | Use |
|:-----|:----|
| Red | Gray signal wire to complete ground circuit. | Allows the spindle lock switch to be a part of estop |
| Black | DCM |  Digital ground signal |

## Wires from the Mesa card ##
|Wire | Meaning |
|:----|:--------|
| Orange       | + of the digital input      |  Provides input to LinuxCNC when the spindle is faulted |
| Orange/white | Ground of the digital input |  |
| Blue         | + of the isolated digital estop out | Provides output from LinuxCNC when the system is estopped |
| Blue/white   | Ground of the digital estop out     |  |


The braking resistor is ~40 ohms.



# Control panel #
A wiring diagram for the HH Roberts analog control panel can be found here:

http://www.hhrobertsmachinery.com/HHRM-docs/Topwell/GL%20220V%20Head%20Replacment%20Manual%20Rev%204A.pdf

or

http://www.hhrobertsmachinery.com/Support/Manual_machine_Parts_Lists/Yaskawa/GL%20Yaskawa.JPG

This control panel was rewired to:

**Use 24V DC relays for the latching enable circuit** Use a different forward/reverse switch that provides independent normally open switches for forward and reverse
**Simplify the wiring for the analog speed input so that it was independent of the enable latch.  This was needed as this drive has separate DC control and analog in grounds.**

The wiring of the latch relay is currently not ideal as the wiring is way over-sided.  Smaller wires with crimp terminals would greatly simplify it and make it more reliable.

# References #
The manual for the VFD can be found here:

http://www.cnczone.com/forums/attachment.php?attachmentid=79285&d=1239132143

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
|Black | VI             | Wiper of speed POT | Analog speed signal in |
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

TODO: Wiring table updated with Delta values

# Drive Configuration #

| Settings | Factory | Set to | Meaning |
|:---------|:--------|:-------|:--------|
|02-00| 0 | 1 | TODO: confirm this is: Forward/reverse signals from the wired inputs |
|02-01| 0 | 1 | TODO: confirm this is: Analog speed in from the wired inputs |

TODO: other tuning changes

# References #
A wiring diagram for the HH Roberts analog control panel can be found here:

http://www.hhrobertsmachinery.com/HHRM-docs/Topwell/GL%20220V%20Head%20Replacment%20Manual%20Rev%204A.pdf

or

http://www.hhrobertsmachinery.com/Support/Manual_machine_Parts_Lists/Yaskawa/GL%20Yaskawa.JPG

The manual for the VFD can be found here:

http://www.delta.com.tw/product/em/drive/ac_motor/download/manual/VFD-B_manual_en.pdf
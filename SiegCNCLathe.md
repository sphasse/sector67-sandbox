# Introduction #

This page describes the conversion of our Sieg KC4S (SC2518) CNC lathe to LinuxCNC.

# Details #

# Existing configuration #

## Spindle Encoder ##

AutomationDirect.com encoder
TRD-S100BD
http://www.automationdirect.com/static/specs/encoderld.pdf

100 pulses per revolution
12-24 VDC input voltage
NPN open collector

This is an after-market part, not stock.

### Open collector connections ###
| White | OUT B |
|:------|:------|
| Orange | OUT Z |
| Shield | Ground |
| Black | OUT A |
| Brown | Power source |
| Blue | 0 V |
Cable shield is not connected to the encoder body;
enclosure is grounded through the 0V wire

Plus a dedicated hall encoder for a Z pulse, LM5-3001A proximity switch


## Stepper motors and drivers ##
### Drivers ###
Yako YKA2404MA

http://www.yankong.com/doce/product/detail_103.html

Motors
YK60HB86-04A




## Spindle motor and drive ##
The spindle motor is a brushless motor with a 500W controller.  This controller is not well documented, but it takes 0-10V analog input and has a forward/reverse input as well.  The controller is basically three components that work together, the "driver" board (XMT-DRIVER-500-A), the "control" board (XMT-CONTROL-500-A) and an input board (XMT-SK) that provides signals to the control board.  Being a brushless motor, there are encoder inputs to the driver and three phase output.

TODO: more details on the controller...

**0-10V analog speed input** TTL direction input

## Mesa hardware ##

| Quantity | Part | Price |
|:---------|:-----|:------|
| 1 | 5I23 FPGA based PCI  Anything I/O card | $229 |
| 1 | 7I37TA Isolated I/O card | $79 |
| 1 | 7I33TA  Quad Analog servo interface | $79 |
| 3 | DIN RAIL ADPT KIT | $5 ea |

# Encoder pulley #
In order to make the Z pulse of the encoder once per rev (a LinuxCNC requirement), I am attempting to 3D print the appropriate 52T 3MM pitch HTD timing pulley using this (hopefully) most excellent parametric model here:

http://www.thingiverse.com/thing:16627

We'll see how that goes...

... It went quite well with a usable part currently mounted on the encoder, with load tests to follow...

# Integration board #
As Mesa did not have the 7i33TA in stock and we needed to use pull-up resistors on the encoder lines in any case (we could have probably done that safely enough with the 7i33TA inline), a small integration board was needed.  This was made from a 2"x3" perf board with a 50 pin interface on one side and screw terminals for the encoder and analog out on the other.

# Build log #
## Nov 10, 2012 ##
Did about 2 hours of work this afternoon cleaning things up to get ready for the LinuxCNC conversion:

  * Removed the existing controller board and stepper wiring
  * Cleaned up some other wiring
  * Created a pncconf configuration of an XZ stepper lathe with spindle
  * Put the 5i23 card in the PC and hooked up a 50 pin breakout board to the P4 connector for driving the steppers

Chris and I made good progress on the stepper control.  We've got the stepper pins wired properly but don't seem to be able to observe step pulses.  In retrospect this is because I had the step rate way too low, it was 200 when it needed to be closer to 10000 (exact values need to be determined).  The pulses were happening but too slowly to register on a multimeter as an increase in the average voltage or to be noticed on the scope.  Better triggering might have show the pulses better.

## Nov 11, 2012 ##
I stopped in for one hour tonight to get the steppers actually moving.  After re-tuning the step rate and configuring the hold times properly (per the datasheet some were 2500us and some were 1000us), stepping now works well.  There is some extra noise, but I need to look at the microstepping and how the drive current is configured to iron that out.  The axes are not fully tuned yet but they do move when commanded.

I would have had it working much sooner if I had the step rates high enough to observe with a multimeter or scope.

## Nov 12, 2012 ##
About 3 hours of work.  Lots of progress tonight working with Adam.

  * Moved the controller board for the brushless drive to a new location, this required tapping some new mounting holes in the backplane.
  * Moved the rectifier for the DC power supply to a new location
  * Mounted a DIN rail for the Mesa daughter cards
  * Wired GND/+5/+12 buses for stepper and encoder support.
  * Cleared out the bottom enough to place the PC in the cabinet, it is a tight fit but just makes it.
  * Wired the 0-10V analog output signal from the mesa card to the spindle controller and verified via pncconf open loop control works properly
  * Wired a breadboard with 1k pull-up resistors to +5V for the encoder and confirmed proper encoder functionality
  * Got closed-loop control working

Things generally went smoothly, however, the spindle scale did have some issues.  I initially had the default scaling to 10 in pncconf with a "reverse spindle" setting causing this to be -10 in the .ini file.  This needed to be closer to -1500 to work properly, and after doing so the spindle speeds (e.g. "S500") were in the ballpark but not exactly tuned.  The spindle is still running in open loop mode and you can hear some delay, for instance undershoot when slowing down.

So many of the major components are working properly (stepper controls, spindle control, encoder input), but just need to be wired more permanently and tuned properly.

## Nov 18, 2012 ##
I spent a few hours on the project today and Chris helped significantly.  We accomplished the following:

  * Soldered up the integration board (described above), wired it in and confirmed proper functionality.
  * Removed the hall sensor and associated steel indicator.  Hopefully this will balance the machine better.
  * Removed the coupling from the X axis stepper motor to the ball screw.  This was a bit of a pain as it was not that accessible.
  * Looked at the software configuration long enough to figure out that my approach to fwd/reverse on the spindle was not going to work.
  * Send a query to the LinuxCNC mailing list asking for alternate approaches.
  * Measured the ball screw thread pitch, on the X axis it is 5mm.
  * Unmounted the encoder and replaced the pulley with the printed one.  Awaiting the belt to mount it again.

Of note was that the X axis was a bit sticky when turning and in fact it was binding and losing steps.  It turns out the coupler was a solid one, and after removing the motor the x axis ball screw seems to turn more easily.  As a result we are replacing the coupler with a flexing one as it seems clear the alignment to the motor is not perfect.

## Nov 20, 2012 ##
A couple more hours invested tonight:

  * Updated to LinuxCNC 2.5 stream.  This required re-doing the pncconf configuration, which was no big deal.
  * Tested the estop.  It basically shuts down AC input.  Somewhat disconcertingly, this is not latching and the failure mode for the estop button is not estopped.
  * Attempted to accurately tune the X axis, but the thread pitch is not the same as the Z axis, so I can either calculate the value or measure the pitch, which will be a pain because it is mostly inside a motor case.
  * The stepper motors ran rough until I re-tuned the step delay settings.  I had forgotten to pull those over when I re-did the pncconf config.  the step and direction hold both needed to be 2500 us.
  * I put the initial config under revision control in SVN

As a reminder, on a typical CNC lathe:
  * When the TOOL moves right, away from the chuck that is the positive Z direction
  * When the TOOL moves toward the operator that is the positive X direction.

## Nov 23, 2012 ##
Two more hours spent today:
  * Adding the abs component to the motion spindle out signal did the trick and I was able to get spindle forward and reverse working properly.
  * However, I needed to configure the spindle to be reversed in pncconf as I was initially getting only negative voltages either direction, when I needed positive.  This setting sets the scale of the mesa pwmgen component to something like -3750, and I then can properly get forward and reverse spindle movement.
  * Speaking of spindle scale, my first guess that the scale should be -3000 was off.  Thankfully the DC brushless control is linear, so I adjusted to the aforementioned -3750 and it is now in the ball park.
  * Spindle at speed doesn't seem to be working though, I need to look into that.
  * I started to look at the auto tool changer.  Should be an interesting project.
  * I figured out that although the Z axis coupler being rigid was probably not ideal, most likely the axis problems I was having were due to me missing setting the 2500us set and direction hold times and so the defaults of 1000us were being used for that axis only.  Version controlled configurations are a nice thing, even if they do implicate you.

## Nov 25, 2012 ##
About 4 hours today, with help from Jim and Paul:
  * Talked through PC integration with Paul and how we will mount a monitor and keyboard.  Started in work on that.
  * Cleaned up the wiring significantly, putting some of the wire duct cover back in place, terminated some wire shorter where it made sense, added a star ground line to the control side of the encoder.  This took quite a while but was nice to get done.
  * Mounted the isolated I/O card
  * Fabricated a DIN mount box for the integration board and mounted it
  * Toned out the limit switches, there are two limit switches per axis so a + and - limit configuration will be possible.
  * Added to the integration board to add limit switch 6k pull-ups to 12V and wired the limit switches to isolated I/O.
  * Jim fabricated a new spacer for the encoder pulley

## Nov 27, 2012 ##
3 hours in tonight making solid progress:
  * Limit switches integrated and working.  The switches had ~5k inline resistance, so I needed to use ~47k pullup resistors instead of the ~5k I used prior.  Some re-solder work was needed on the board as a result.
  * I struggled through my typical mapping of isolated I/O to pncconf values, but am getting better at that.
  * Software-wise the over-ride limits does not seem to be working properly.  Once I job onto the limits I can't get off of them without going to open loop via pncconf.  I'll need a solution for that.
  * I played a bit with a PID loop for the spindle and had a slow response working OK, but when I hit stop in the manual spindle control it seems to want to run away.
  * So that is disabled now, with some more playing needed.
  * I temporarily added an OPEN\_FILE = <lathe pawn demo> so that a useful lathe demo file is loaded at startup.
  * The spindle encoder is now mounted more safely and sanely.  I ended up just press fitting the pulley to the encoder shaft which I think should be sufficient.  Time will tell, and a drop of epoxy would probably not hurt.

## Dec 2, 2012 ##
Again solid progress, 4 hours spent:

  * Re-integrating the PID loop and tuning it to be at least close to the open loop control.  More tuning might bear fruit here, I have just ff0 and I tuned currently.
  * Figured out the X scaling to be a somewhat odd number (25736.5).  At 1.8 degrees per step, 10x microstepping this does not result in a thread pitch that seems off-the-shelf, but I did measure it getting backlash out of the system, etc., and I believe my dial indicator is good.
  * Solved the limit issue.  Firstly, I did properly have home+limit configured per advice on the linuxcnc mailing list, but I was setting the home location such that it thought it was at the soft limit in one direction and was at the hard limit in the other direction.  Fixing this such that the limit switch was located properly allows a homing to prevent hitting any hard limits.  I gave myself a bit of X negative direction to allow the default pawn program to run and presume some amount of z negative for facing, etc. might be typical.
  * Configured reasonable values for X max accel and speed, primarily just listening to the motors once I got the scaling correct.
  * Fixed the spindle at speed LED never lighting green.  I believe this is a pncconf defect that needs to be followed up on.
  * Added to the small post-fix.sh sed script to change the default file to the pawn, and to fix a number of other small issues so I am not manually re-editing after pncconf.

Paul has also done a nice job integrating a monitor stand, a through hole for the keyboard, etc. and a power switch for the pc on the outside of the case.

## Jan 26, 2013 ##
Lots of progress since the last update several parts made successfully, and I'm working out tooling and tool table issues.  I worked on the Z axis today, confirming that an inch in software really does equal an inch in real life.  Some issues:

  * Having both switches as home + limit min sometimes makes homing not work, as the "first" home switch is the one configured to be used when homing.  If this is not the proper one to use, the home process will override the limit switches and run off the end.
  * There was independently an issue with the with the X limit switch where at the max limit the min limit switch was sometimes triggering as well.  The switch needed to be adjusted a bit to resolve this.

Tasks to do:

  * Increase the Z max velocity, attempt to increase the max acceleration.
  * Determine a sensible Z=0 relative to some part of the cross slide.
  * Document the tool table meanings.
  * Document a new tool procedure, including "Machine->zero coordinate systems->P1 G54" before tool adjustment.
  * Add a USB extender cable to be able to use a thumb drive to transfer files.

## Feb 2, 2013 ##
More good progress, first large test queen part.  Learned that I probably need to keep the roughing tolerance at tool radius + some small amount rather than just the tolerance itself.  First one-hour cut was a bust due to the roughing cuts being tool close.


## April 6, 2013 ##
Taught the Beta 2 version of the class to Joe, Josh, Micah and Mark.  Two hour class.  The curriculum is getting there, need more software examples and more things worked out through the software path.

# TODO hardware #

  * X Take the front panel and USB connectors off of the front of the case and figure out how to attach the external components to the PC (power, keyboard, mouse, monitor, external USB)
  * Figure out an approach for powering the PC, should it boot when the machine boots or independently.
  * X Test the spindle at speed signal working (why is it always red -- answer: no pyvcl pin mapped by default?).  Filed as a bug: https://sourceforge.net/tracker/?func=detail&aid=3592225&group_id=6744&atid=106744
  * X Integrate a PID loop to the spindle control.
  * X Integrate the limit switches
  * Integrate estop
  * Integrate machine on, perhaps add a relay inline
  * X Look at the stepper drive configuration for current and microstepping to try and make the stepper drives smoother.
  * X Configure proper stepper scaling for both X and Z and confirm with a dial indicator
  * X Figure out and configure the correct spindle and spindle encoder scaling
  * X Wire up a forward/reverse signal for the spindle, configure such that negative voltages cannot be generated
  * X Order, make or print a 3mm pitch 52 slot 6mm bore encoder pulley
  * X Mount another DIN rail for the DC bus
  * X DIN mount the isolated I/O card
  * X Trace out the limit switches to see if they are functional
  * X If so, wire them to the the isolated input card, probably with +12V pullup.
  * X Confirm the default plane is XZ
  * Add space bar as a pause (see sheetcake project for steps)

# TODO Software #
There are several next steps with CamBam and software integration:

  * Document the constant surface speed spindle setting, how to do it manually
  * Investigate if there is a CamBam-based way of doing constant surface speed
  * Investigate what it would take to create the proper tool configuration in CamBam (zero diameter, proper tool description) matching the actual lathe tools
  * Can we provide a machining op style?  Is that too much "magic"?
  * Figure out how to do negative X moves in a CamBam tool path
  * Provide a table of reasonable Al speeds and feeds, plunge depths, etc.
  * Is there a way to change the post-processor or tool/machining OP headers/footers to add G43 on tool changes?
  * Is there a way to change the post-processor or tool/machining OP headers/footers to add G41/G42 on right/left hand cutting?
  * Figure out how to do a parting operation in CamBam (fake drill op in XZ plane?)
  * Create a documented demo of a chess pawn from nothing to completed part.
  * Put the rest of the tools in the LCNC tool table and calibrate them (straight on 60 degree, threading tool, parting tool, others)
  * Document the settings in the tool table and how they can be adjusted properly to tweak slightly wrong tool alignment.
  * Consider ordering a 20/70 degree tool for testing.
  * Determine how we would do facing and boring operations using CamBam.
  * Test threading and document common threading cases, specific diameters and pitches for ANSI and pipe threads.




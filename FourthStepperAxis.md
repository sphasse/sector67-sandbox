

# Introduction #
[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/complete\_table.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/complete_table.JPG)

_The assembled table_

As we started to implement 4th axis capability for our mills in earnest, we acquired a 8" horizontal/vertical rotary table with a stepper motor already integrated.  This led us to transition our effort away from the servo-based fourth axis described at FourthServoAxis to a stepper-based system.  It's a testament to the flexibility of LinuxCNC and our implementation that this really won't cause us to change much at all with respect to the implementation.

It has given us a chance to work out most of the issues associated with integrating a stepper into our servo-based system.

# Stepper driver #
The stepper drive we are using is labled DS335, and we were able to find datasheets and some integration information for it here:

http://www.interinar.com/ds335.html
http://www.interinar.com/public_docs/DS335.pdf

It will provide up to 3.5 amps and is designed to be optimally run at 36V.  It has optically isolated inputs designed to run with no resistors at 5V, and expects step and pulse inputs as well as +5V.  Motor timings are somewhat cryptically described as "5 uS", presumably for all values.

# Stepper motor #
The motor supplied is a NEMA 34 frame size stepper that otherwise has absolutely no specifications on the motor itself.  The phases are non-tapped, TODO: get Ohm resistance, and the motor seems functional with a 3.5 amp controller at 36 volts.

# Rotary table #

[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/whole\_assembly.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/whole_assembly.JPG)

_The rotary table exploded_

## Basic mechanics ##
The rotary table we are using is a basic 8" horizontal/vertical table with a direct-drive stepper motor adapter and coupling of Chinese manufacture.  We took it apart to asses our backlash tuning options and just to see how it worked.  The table turns on ground beds that have elliptical channels for distributing the grease.

[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/table\_underside.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/table_underside.JPG)

_The underside of the rotary table showing the gear teeth_

[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/table\_bottom.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/table_bottom.JPG)

_The base of the rotary table_

The turntable itself is held in place by a large threaded ring on the back of the turntable.  This ring is half split, presumably to provide some spring loading to hold the table in place.

TODO: picture of this nut

The table is turned by a worm drive that meshes with screw teeth around the inside perimeter of the turntable.

[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/screw\_shaft.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/screw_shaft.JPG)

_The screw shaft assembly_

## Backlash tuning ##
This table has two major sources of potential backlash.  Firstly, if the worm drive shaft moves back and forth this will introduce backlash.  This is supposed to be prevented by a thrust bearing inside the table and a shaft collar outside the table holding the worm shaft secure.  Unfortunately, the shaft collar could not actually be turned to hold the worm shaft tight, so some minor changes needed to be made to that.

The second potential source of backlash is the worm drive teeth meshing with the gear on the turntable.  The worm drive has no support on the internal end and runs in a bushing whose center is eccentric to allow backlash tuning:

[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/eccentric\_bushing.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/eccentric_bushing.JPG)

_The eccentric bushing_

The tightness of the worm drive to the gear and be changed by rotating the bushing, which moves the spinning shaft closer or further.  Once the bushing is aligned appropriately, it bushing is held in place with a screw labeled for backlash adjustment:

[http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/thumbnails/bushing\_and\_bearing.JPG](http://sector67-sandbox.googlecode.com/svn/trunk/ProjectSheetCake/docs/images/fourth-stepper-axis/bushing_and_bearing.JPG)

_The busing and bearing.  The backlash adjustment screw is just out of this picture.  The thrust bearing shown in this picture could not be used as the diameter was too large, so it was replaced with a bushing._

This nut serves no useful adjustment purpose with this device coupled to a motor (although it is needed to hold the eccentric bushing in place), so the thumb screw should be replaced with a set screw so that the adjustment is not messed up by accident.  I was not able to find a suitable replacement set screw so this was not done.

If this rotary table had a simple hand wheel for turning the table, this backlash adjustment mechanism would probably be helpful, but since they adapted the direct drive shaft to it, the motor coupling needs to be attached in a fixed location.  This means you can tune the backlash once via the eccentric bushing.  This was done at the factory, and then holes were drilled and tapped for the motor adapter.

Well, actually it was done three times (at the factory?) as you can see that the holes were aligned three times and twice bolts were screwed in and ground off.  Thankfully the final location of the motor mount holes allowed the eccentric bushing (when turned CCW) to mesh tightly with the turn table.  In the picture above showing the busing and bearing, you can make out a few of the ground off bolts used to fill the holes presumably after bad backlash tuning efforts.

You can only put so much lipstick on a pig, but we've ordered two sets of pin thrust bearings, one to replace the existing mostly frozen bicycle-style ball thrust bearings inside the table.

The second set was supposed to go on the outside of the shaft where previously a shaft collar (with a set screw that tightens directly onto the adjustment threads) just rode directly on the end of the bushing.  Unfortunately, the diameter of the thrust bearings was too large to use with the motor coupler, so I just turned down a brass bushing instead and put that in place.

Additionally, I filed a flat spot at the appropriate location on the threaded portion of the worm shaft so that the set screw in the threaded collar did not mess up the threads, preventing future dissassembly and re-tuning if necessary.

The new thrust bearings were a bit thinner than the stock ball bearings, so the worm shaft sticks out a bit more than previous, which is causing the motor not to fit tightly to the motor coupling.  For the short term, we've used washer spacers and will cover the gap with metal duct tape.  In the long term, putting some more spacer washers on the inside portion of the worm shaft would resolve this issue.

Once re-assembled with these adjustments there was very little backlash.

# Motor/table integration #
Since the system already came as an integrated unit, this was very straightforward.  The stepper shaft is attached to a coupler that drives the worm screw directly.

The stepper motor we're using should have plenty of torque to run the table, even with the relatively lower-power stepper driver we're using.  High end speed might not be that good, but generally that is not too much of a concern for a CNC rotary table.

The coupling casting could use some refinement as well, with the crinkle coat on the end facing the table needing to be machined off and some of the access holes for set screws could be enlarged a bit for easier access.

I did somewhat enlarge the access hole for the 3mm hex head motor coupler screws, as the existing hole did not allow access to the set screw.

# Table/chuck integration #
The table has a (TODO: get taper) center spindle, and the table has four T slots at 90 degrees from one another for mounting things.  In practice it is helpful to have a chuck for clamping.  This section describes mounting a four- or three-jaw chuck.

## 8" four-jaw chuck ##
Our larger lathe has 8" chucks and the independent four-jaw chuck has four mounting holes, making it convenient for mounting to the rotary table.  The only challenge was to find T nuts the right size for the T slots, and to find Allen screws appropriate for recessed mounting of the chuck.

## 6" three-jaw chuck ##
We also have a 6" three-jaw that can be mounted.  The three-jaw chuck has 3 mounting screws at 120 degrees, so it does not directly match with the rotary table.  As a result an adapter plate is needed to attach the chuck.

TODO: once the adapter plate is working, document.

## Centering work in a four-jaw chuck ##
Some helpful resources for centering work in a four-jaw chuck:

http://littlemachineshop.com/Reference/Centering4-JawChuck.pdf

http://www.youtube.com/watch?v=2KMhx4DbyDg&noredirect=1

# Electronic integration #
Our stepper driver requires ~5V signals for proper signaling.  The Mesa 5i23 card has jumpers settable for 3.3 or 5 volt pullup, and I configured the card for 5 volt pullup for this driver.  In the end I now have all three jumpers (on all three connectors) on the 5i23 to be in the "up" position in order to properly pull up to 5V and reliably signal the stepper driver.

# LinuxCNC configuration #
To configure LinuxCNC, we needed to add some stepgens to the configuration.  This can be done using the pncconf configuration generator.  Since typically we'll be running in three-axis mode (XYZ), we'll make a separate configuration for a 4-axis rotary table configuration (XYZA).  TODO: document the option to get 4 stepgens... Unfortunately, pncconf clears out most of the PWMgen/encoder/stepgen configuration when you reconfigure the mesa driver configuration, which required me to re-enter the encoder and PWMgen configuration for the XYZ axes.

Using the new configuration, we can integrate the stepper A axis by choosing a stepgen (on the second connector, somewhat confusing labeled "connector 3" TODO: confirm) as the A axis.  The pins corresponding to the pwmgens, encoders and stepgens are automatically allocated by the hostmot2 driver, and that is why we configured arbitrary I/O on the third connector, so the first two would be free for this "automatic" allocation.

To see what 5i23 pins this actually resolves to, you can look at the output of the dmesg command.

TODO: capture example dmesg output here, showing which pin is pulse and which is dir

The pncconf tab for assigning A axis to the stepgen is shown below:

TODO: screen shot of the pncconf allocation tab

And the actual axis configuration is shown below:

TODO: screen shot of the A axis configuration page

The values were arrived at the following:

1) The step and direction delays are conservative based on the somewhat vague datasheet which lists "5 ns" value for delays.

2) The scaling was calculated by manual measurement of the rotary table and degrees per step.  The values were confirmed when then table was completely assembled by using MDI commands in LinuxCNC.

We were occasionally encountering joint 3 following errors at the end of a move, after deceleration.  I reconfigured the following error on the A axis, configuring it for MIN\_FERROR of 0.005 and FERROR of 0.05.  After doing this, the joint 3 following errors were resolved.

## LinuxCNC Axis GUI integration ##
Currently, I don't believe the axis GUI is not properly plotting 4th axis operations.  Although I have only done the operations treating the surface of the cylinder as Z=0, which would make all milling operations appear on a single line.  I need to try backplotting a part with the Z=0 set to the center of the cylinder.

# 4th rotary axis gcode generation #
After getting the hardware in place, I had hoped this would be relatively straightforward.  It turns out there are not very many readily-accessible open source solutions for generating 4th rotary axis gcode.  There are of course high-end commercial solutions:

TODO: links

and some lower-end commercial solutions:



One basic approach is to generate gcode for the XYZ axis and then convert the Y axis to be the A axis.  This is in essence wrapping a flat milling operation around a cylinder.  There are some considerations when taking this approach:

1) The Y axis units are linear and the A axis units are degrees, so the scaling is quite different between the two.  You can scale the drawing to reflect this (e.g. 180 units would be half of the cylinder), but this means that any sort of cutter compensation will not work correctly.  For instance pocketing operations, etc. would be slightly wrong.

2) 3-dimension arcs (e.g. spirals) are configured in a plane that is declared in the gcode.  Those would not be handled properly via this naive approach.

There is perhaps a conceptually simple solution in re-scaling the A axis in LinuxCNC so that Y axis units make sense when interpreted as degrees, but that would require re-configuring LinuxCNC scaling for each 4th rotary axis project, and since velocity and acceleration are involved in that, it could be somewhat complex.

This did not work, but the GEOMETRY section in the ini file likely needs to be configured to properly display the A axis.

# Build log and lessons learned #
## 5V pullup or the 5i23 ##
In my initial integration, I thought I failed to set a scaling number before testing and so the motor was not moving during simple open loop testing.  It turns out this was not the case, and that the motor was not moving because the Mesa card was configured for 3.3V pullup and the stepper driver required 5V pullup.  There are three jumpers on the Mesa card, and two of the three needed to be set for 5V to get a 5V pullup.  I have now moved to having all three jumpers set to the 5V position.

## Stepper driver overheating ##
We are running the stepper driver at its max current setting, and as a result it gets hot if not cooled by a fan.  It will start to malfunction when it gets hot enough.

## Acceleration and max velocity values too high ##
These still need to be tuned completely as they are currently too high.  LinuxCNC currently allows the A access to be driven such that the motor gets to a bad oscillation state, runs backwards for a bit and then whines.  Originally I thought this was a driver overheated state, but it turns out it was LinuxCNC being configured to allow too high of a velocity.

Turns out it might not have been that, and this is still somewhat of a mystery.  I cannot drive the machine to oscillation by maxing out the velocity, so either the test program hit an oscillation velocity or there is some other problem.  This still needs to be determined.

## Stepper axis "joint following error" ##
TODO: document why this happens and how to resolve it.  One cause was following error too low.  After modestly upping the following error values we were able to resolve this.

## Test 4th axis program ##

## Procedure for testing backlash ##

# TODO #
There are still several tasks remaining to complete this project fully, including

  * Solder up the motor cord end with the 5-pin XLR connectors from probotix
  * Drill a hole and mount the 5-pin XLR socket in the back of the right case for connecting the rotary table.  There might already be holes in the back of the cabinet, there are in the 3300 mill cabinet anyway (consider mounting this in the 3300 mill?).
  * Fix the cord where it is enters the housing on the motor as it is extremely twisted from previous abuse.  Consider some sort of strain relief or conduit for that connection.
  * DONE 1/22/2012 Cover the gap in the motor mount with metallic tape (5 minutes)
  * or fix the shaft length by adding washers inside the bushing (~1 hour disassembly of the entire rotary table)
  * Fix the acceleration and velocity max settings in LinuxCNC so that the motor cannot be driven too fast.  I tested with the current settings but
was unable to drive the table to a bad state like the gcode file was (e.g. G01 A90 F10000 maxed out at a feed rate of 1000 properly.  I'll need to review the gcode file.
  * Get the LinuxCNC configuration for four-axis milling under revision control in SVN.
  * Get the values hand-edited in the conf and hal files back into the pncconf so that future tunings can be made via pncconf
  * Write a procedure for rotary table usage and post it to the internal sector67 wiki
  * Post our test A axis gcode for public accessibility.
  * Generate some more compelling A axis test gcode
  * Correct the GEOMETRY settings in the ini file so that the A axis backplot works.  Consider if this is a bug in pncconf that should be fixed.  GEOMETRY=axyz seems to be working a bit better but needs to be verified.
  * DONE: Wire up the 36V supply instead of the bench supply.  The table still works fine with the new supply.
  * Mount the 36V supply and stepper driver in the right cabinet.  This will require tapping into the estopped 120V power, ideally after the fuses.  After we remove the current extraneous 5/15V supply, we should have space for the 36V supply, but we might need to get a bit creative to find a spot for the stepper driver in the right cabinet.
  * Tackle the wiki inline TODOs above this to complete the existing documentation
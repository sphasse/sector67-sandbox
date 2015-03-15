

# Sector67 Sieg CNC Lathe Introduction #

Sector67 (http://www.sector67.org) recently acquired a Sieg CNC lathe with motors and amps but without a controller.  We integrated a LinuxCNC control system and are in the process of making the lathe ready for production work.  This document provides an overview of some of the concepts needed to understand and properly operate this lathe.  The document was written by Scott Hasse, who did most of the LinuxCNC controller integration, and is from the perspective of, and will be most useful to, someone basicaly familiar with manual lathe operation and operation of our CNC mills (CNC mills without an automatic tool changer).

There are significant differences in tool handling and tool pathing between lathe and milling operation.  Most CNC lathe jobs will have one or more tool changes, so accurate tool descriptions and consistent changes become much more important than when working on a mill.  Comparing tool changes on our [R8](https://code.google.com/p/sector67-sandbox/source/detail?r=8) collet Bridgeport-class CNC knee mills to the CNC lathe:

  1. On a knee mill when you make a tool change you can use the knee to manually re-adjust the tool offset (typically a length/Z offset) without changing the offsets in software.  There is no equivalent manual adjustment facility on our lathe.
  1. When changing tools on the mills only one axis (Z) needs to be adjusted.  Typically with a lathe tool change there are offsets in two dimensions (X and Z) that need to be applied.
  1. The tool footprint for milling operations is nearly always a cylinder or at least radially symmetric, making tool compensation when calculating machine paths relatively simple.  This is generally not true for lathe tools.

These differences complicate tool handling when working on a CNC lathe.  When working on a manual lathe (measure->cut->measure cycle) it is simple enough to adjust your work manually, but for a CNC lathe these operations need to handled programmatically.

This document describes one path for generating accurate CNC lathe tool paths.  There are certainly other ways of doing this, and our approach might evolve over time.

## Tool changer choices ##
As part of the lathe acquisition we also acquired a motorized four-position tool turret.  In theory this could be integrated fairly simply using our Mesa hardware and LinuxCNC software to provide automated tool changes.  We also had a spare AXA quick change tool post available.  Choosing between the two, our initial strategy has been to utilize the AXA quick-change tool post for a number of reasons:

  1. With this approach we are not limited to four tools, and it is easy to envision more than four tools needed (at least left, right and straight cutters, threading grooving and parting).  Facing versus turning will also add to the tool count.
  1. Although unattended operation would in theory be great, it is not very likely we will be running many jobs unattended.
  1. AXA tool holders are cheap and readily available.
  1. The tool changer is currently a bit high for directly fitting tools, so some mounting adjustment would be needed
  1. The tool changer currently runs off of 3-phase 240V, and we didn't want to introduce those power requirements to this small lathe

All that said, in the future it may make sense to integrate the automatic tool changer for some jobs.  We have ample I/O, and it would be simple to convert the changer to use a small stepper motor.

## Tool choices ##
We are for the most part committed to using carbide insert indexable lathe tooling for the CNC lathe.  There are many circumstances where carbide tooling is not appropriate or does not provide the best cutting experience.  However considering many factors including our intended user audience and need for accurate tool offsets, overall it seems to make the most sense for us to make use of insert-based tooling.

## CNC Lathe Concepts ##
This section contains some concepts that are important to understand when working with a CNC lathe:

### XZ Axes ###
The Z axis is the longitudinal axis, while the X axis is the cross slide axis.  One intuitive way to think of this is that the Z axis is parallel with the spindle for both mills and lathes.

### Tool path ###
This is the programmed motion of the tool.  Depending on the machine configuration it is not always followed 100% accurately, but the goal is that the tool will generally follow the tool path.  It is important to understand that, due to tool size and geometry, the path the tool follows is different than the path that is cut on the part.  The difference beween the tool path and the part cut is known as cutter compensation.

### Tool control point ###
This is the point relative to the tool that will follow the programmed tool path.  For a flat mill end, this would typically be a point in the center of the bottom of the tool.  For a lathe tool, it is more arbitrary and needs to be defined.  For example for a triangular cutter the control point would traditionally be a point tangent to an X and Z cut done by that tool (which is probably not the vertex of the triangle), even though for cutters with a radius that point is off of the actual tool.

[This document](http://www.linuxcnc.org/docs/2.4/html/lathe_lathe-user.html) has a much better and graphical description of the tool control point.

### Tool table ###
This is a text file stored with the LinuxCNC configuration that defines the tools in use.  There is a GUI editor for this text file.  The file contains information such as the offsets in the appropriate axes to the tool control point, the radius of the cutter and other tool meta data that LinuxCNC needs to properly perform cutter compensation.

TODO: understand and document the values in the tool table (radius/diameter??).

### Cutter "front angle" ###
This is the angle of the "front" of the cutter in degrees from zero (Z+) direction

### Cutter "back angle" ###
This is the angle of the "back" of the cutter in degrees from zero (Z+) direction

### Left hand and right hand cutting ###
To me these seem reversed from what would be intuitive.  For a normal lathe setup, "right hand" cutting is with the tool moving to the left and "left hand" cutting is with the tool moving to the right.  Understanding this properly matters when defining different cutting paths in software.

One way to think intuitively is which side of the path is being cut.  In a right hand cut the material is being cut away on the right hand of path of motion.  For a left hand cut, the material is being cut away on the left hand of the path of motion.  Thinking of it this way can simplify cutter compensation configuration.  Thinking of it this way also translates to right and left hand cutter compensation for milling operations.

### Cutter compensation ###
Cutter compensation is the difference in motion between the tool path and the extents of the part that is actually cut away as intended by a real cutter.


## Generating cutter compensation ##
The basic choices when using software to generate the tool path are:

A) Tell the software about the tooling and let it generate appropriately compensated tool paths.

B) Have the software use zero radius tools and have LinuxCNC perform cutter compensation.

Complicating this is that our current tool for generating lathe gcode (CamBam) does not officially support lathe tool compensation, although it will create a path compensating for a circular cutter.  So, as long as we can approximate our lathe tools with circular cutters, and compensate ourselves for angles that cannot be cut, we could do tool compensation in CamBam.

Alternatively, we can program the direct path (zero radius cutter) in CamBam or other software and have LinuxCNC perform cutter compensation.  The most significant change in this case is that LinuxCNC needs to know if the movement is a left hand or right hand cut and introduce appropriate gcodes such that the correct compensation mode is in place as appropriate.

In fact since both approaches are viable we could support both approaches.  However, there is a small but critical difference in how the tool table is set up for cutters with a radius.  In the case of LinuxCNC cutter compensation, the tool control point should be at the point of the tool tangential to the X and Z cuts the tool makes.  If CamBam is considering the tool when doing path generation, the tool control point needs to be the center of the cutting tool radius.  This makes a significant difference in the tool configuration procedure or when entering data into the tool table for X and Z offset.  So generally we need to pick one method and stick with it, or have two definitions for each tool with different control points.

The approach we are currently taking is to have LinuxCNC perform cutter compensation.  Most significantly, this simplifies tool setup at the cost of some gcode complexity.  Once we have some more experience under our belt we'll re-evaluate this approach.  For instance if we get access to more sophisticated lathe path generation software in the future, we'll have to evaluate its capability to perform tool compensation.

An additional plus to this approach is that conversation/MDI lathe operations done live at the console make sense, and the LinuxCNC axis GUI is an accurate DRO.  With the tool control points set differently that would not be the case.

## Procedures ##
This section describes some of the procedures to follow when calibrating tools, testing tool calibration, generating gcode and running jobs.

### Calibrating a tool in the tool table ###
It is very easy to make mistakes when performing this procedure.  In particular it is very simple to use the wrong offset when touching off toos and to forget to use a G43 to apply cutter compensation.  To reduce this risk, our ideal vision is to have a set of known, calibrated indexable tooling so that we can home the machine, touch off the Z axis and run jobs without needing to calibrate tools at all.  However, if you need to calibrate a new tool, this section gives the procedure.

To calibrate a tool properly in the tool table (adapted from http://www.linuxcnc.org/docs/2.4/html/lathe_lathe-user.html):

#### X axis ####

  * Start LinuxCNC
  * Home each axis if not homed.
  * Clear any other offsets (Machine-> Zero Coordinate System -> P1 G54)
  * Set the current tool with "Tn M6 G43" where "n" is the tool number.
  * Put the machine into diameter mode (MDI window, run a "G7")
  * Select the X axis in the Manual Control window
  * Take a test cut and measure the diameter
  * Select Touch Off and (IMPORTANT!) pick "Tool Table" then enter the your calculated tool control point X value.  Ensure that you are entering a diameter measurement in diameter mode.
  * Run a G43 to apply the new offset.  The DRO should reflect your measured value.


For tools with multiple possible control points (e.g. a parting tool), you should pick the most logical one.

#### Z axis ####

  * Start LinuxCNC
  * Home each axis if not homed.
  * Clear any other offsets (Machine-> Zero Coordinate System -> P1 G54).  This is very important.
  * Set the current tool with "Tn M6 G43" where "n" is the tool number.
  * Select the Z axis in the Manual Control window.
  * Make a test cut with the tool.
  * Measure the distance from the face of the chuck to the test cut.
  * Select Touch Off and (IMPORTANT!) pick Tool Table and set the position to the measured distance from the face of the chuck.
  * Run a G43 to apply the new offset.  The DRO should reflect your measured value.

### Ensuring tool calibration with a test part ###


### Generating a path in CamBam ###
This section is largely cribbed from:

http://www.cambam.info/doc/plus/cam/Lathe.htm

As as the CamBam support for lathes evolves we may need to adjust these steps.  The first step is to generate the profile you want to cut.  When doing so, you should treat Y=0 as the center of the axis and draw the profile below the Y axis (negative Y space).  The profile should not cross the Y=0 line and for each cut should be one continuous polyline.  This is done by joining the relevant sections together with a small tolerance.

When generating the profile(s) for cutting, you need to keep the cutting tool geometry in mind.  For instance, some of our most common roughing cutters will be (TODO: spec) 60 degree triangular left and right hand cutters.  With these tools one edge can cut at 90 degrees (perpendicular to the spindle), but the other edge cannot be more steep 30 degrees relative to the spindle or the tool will gouge when attempting the cut.

To successfully cut parts you may need to create multiple profiles and lathe operations with different tools keeping these limitations in mind.

Each of the following should be done for lathe operations in CamBam:

Machining Level:
  1. Ensure the "Machining origin" is a point set along the axis of rotation.  This should be the case by default and typically does not need to be changed.
  1. The EMC2-Turn post processor is selected in the Machining properties.

For each machining operation:
  1. Ensure the "Clearance plane" is greater than the radius of the stock.  You should allow yourself at least 1/4" of clearance to ensure tool changes can happen properly.
  1. DepthIncrement and feedrates are appropriate for the material.  See the speeds and feeds section below for advice.
  1. Ensure the "Stock surface" equals the radius of the stock for that lathe operation.
  1. Set the "Workplane" to XZ.
  1. Ensure the correct Lathe Cut Direction is specified per the cut direction specification above.
  1. Ensure the correct "Roughing/Finishing" option is set.  Roughing will make multiple rough cut passes at the "Depth Increment" and finish with a cut along the profile leaving a RoughingClearance tolerance.  Finishing will make just one pass along the profile.  It is typical to have two operations for each profile, a roughing operation followed by a finishing operation.  With that approach, feeds for roughing operations can be higher and the feeds for the finishing operation can be lower for a better surface finish.
  1. If Roughing, a small RoughingClearance value is set.  This should be set to leave enough material for the finishing pass to make a clean cut.  Carbide is not great at shaving off tiny amounts, so it is a good idea to leave some roughing clearance in the roughing operation.
  1. Define the stock object if needed.  This is typically not needed if you set the stock surface properly.
  1. Set the "Tool diameter" to zero, as we are having LinuxCNC perform the cutter compensation.  This may need to be re-done after choosing a tool number.
  1. Ensure the appropriate tool number is chosen.  Refer to the tool table in LinuxCNC or below.
  1. Ensure the "Tool profile" is set to Lathe.

I have encountered problems with CamBam when a profile crosses over the line at Y=0.  The problem manifested as roughing cuts that were too deep regardless of the roughing clearance setting and in roughing cuts that covered the entire stock regardless of the profile.  As a result, I now make sure that my profiles end at Y=0 in CamBam.  This causes a problem however, since with radiused tools to face off an end for instance you typically want to cut past the center axis a bit or a small nub is left.  A solution to this needs to be developed.

Once you have one machining operation configured, you can copy it for additional operations, changing the primitive ID's, lathe cut direction, roughing/finishing, tool, etc.  CamBam does have styles but they do not transfer with the CamBam file, so they need to be installed separately, which makes them somewhat of a hassle.

Giving each machining operation a distinct and descriptive name will make it easier to find the various operations in the generated gcode, as the names are added to the gcode in comments.

It is typical for CNC lathe parts to have Z=0 be the right hand edge of the part, so you may want to lay your part out in the lower left quadrant.  There are numerous design considerations, including:

1) You may want to have a short lead-in segment at radius=0 so that the tool cuts in from the edge.
2) You need to consider if your tool can actually cut the profile, and divide your job into multiple machining operations if not.
3) The lead-out of your part should be back to the radius of the stock.  If you need to part off, that currently needs to be done separately.  If you need to have the left side of your part have a small diameter, machine the right side first and then have a separate machining operation for the more delicate portion.

### CamBam gcode generation ###
IMPORTANT:  There are manual changes needed after gcode generation with CamBam.  If these are not done you could damage your stock, the tools or the lathe.  This section describes that procedure.

Ensure that after each tool change (TnM6) there is a G43 to apply the appropriate tool offsets.

For instance, the G43 blocks below are added correctly after each tool change:

```
...
T1M6
G43
...
...
T2M6
G43
...
```

We are investigating what it would take to modify the EMC2-Turn post processor to add a G43 after each tool change, so in the future you might be able to modify the post processor to do this for you, but for now this must be done manually.

For left hand cutting operations, ensure a G41 is run in your gcode file before the cuts are made.  For right hand cutting operations, ensure a G42 is run in your gcode file before the cuts are made.  You will have to add these manually.  To simply modifying the gcode, I name each machining operation with LH or RH so that I can find the appropriate comments in the generated gcode.  Again, there is a possibility that we could modify the CamBam post processor to add this capability, but that will take some time.

The G41/G42 needs to be added after the G18 XZ plane mode setting.


### Cutting a part ###
Use the following procedure when cutting a part.

  1. Turn on the machine PC and lathe (the lathe is turned on by disabling estop).  Ensure the tailstock is loose and at the end of the bed and that the machine is generally in good working order.
  1. Start LinuxCNC (Sieg lathe icon on the desktop), cancel estop button in software and enable the machine in software
  1. Home all the axes.  The machine is currently configured such that it will not run gcode or MDI operations without being homed first.  The hope is that this prevents running jobs with the machine unhomed, which could crash the head.  This is done by (TODO: menu operation)
  1. Load your stock and make sure it is properly supported.  You should load your stock after homing so that the homing operation does not crash.
  1. Transfer and load your gcode file.  You can transfer files via email or the USB extension near the monitor.
  1. Ensure the tool that LinuxCNC thinks it has loaded is the tool that is actually loaded.  LinuxCNC shows the tool it believes it has loaded in the bottom status bar.  The physical tools are labeled on the AXA tool holder.  If the tools do not match, you can correct this by running TnM6 in the MDI tab where n is the number of the tool that is actually in the machine.
  1. Switch to the MDI tab and execute a G43 to apply tool offsets.  If the proper tool offsets are not in place when you touch off your part in the next step, you could damage your stock, the tooling or the lathe.
  1. Touch off the Z axis to the proper location to cut your part.  To do this, jog the machine to a known Z location on your part (for instance the faced end of the stock) make sure that the (TODO: get proper instruction) type of offset is selected, ensure the Z axis is selected and choose "Touch Off".  Ensure that the "TODO: get" option is selected and type in the known Z location.  For instance, if I was cutting a part 2" long with Z=0" defined as the right end of the part I would jog the tool to the faced end of the part and touch off Z as 0.0.  If I was cutting a 4" long part with Z=4" defined as the right end of the part I wuold jog the tool to the faced end of the part and touch off Z as 4.0.
  1. After doing this, confim that the tool location in the backplot window (graphical display) is correct relative to the part you are cutting.  As a sanity check, the tool profile shown in the backplot should also match the loaded tool.
  1. Close the lathe door
  1. Hit the play icon to start cutting.
  1. You can pause the program with the space bar or pause button, but it will not stop the spindle.  TODO: check if you can stop/start the spindle with MDI when paused.


### Common problems ###
TODO: document


### Our tool table ###
The most accurate tool table can always be found on the machine itself.  For starters, though, our tools are:

|Tool | Description |
|:----|:------------|
|1    | TCPT32.52 insert 60 degree right hand cutter |
|2    | TCPT32.52 insert 60 degree left hand cutter |


### Practical limitations ###

  * In a trade-off between rigidity and stock size, the tools are generally set up for stock around 2.5" maximum diameter.  In theory stock up to 4" diameter could be cut.
  * The throat of the lathe and chuck will accept stock up to 1" in diameter.  Wider stock will not fit in the throat.
  * <speeds, feeds>
  * If you wish to support stock with a live center, it should be about 12.5" long.
  * We currently only have a 3-jaw 4" chuck, but are looking for a 4" 4-jaw chuck.


## Speeds and feeds ##
When cutting on the lathe, the surface speed of the material being cut as it encounters the cutting surface is a critical factor in effective cutting.  In fact this is true when milling as well.  What makes a lathe different is that the surface speed varies with the diameter you are cutting, so a constant RPM will typically result in a variable surface speed.  LinuxCNC can compensate when using the <TODO: get gcode> constant surface speed gcode

## Understanding carbide inserts ##

For the CNC lathe we will be for the most part making use of indexable carbide tooling.

http://www.homemodelenginemachinist.com/attachments/f13/59299d1356359417-what-size-triangular-inserts-insertnomenclature.pdf

or for more detail:

http://www.ccpa.org/pdf/B212_4.pdf

Taking a common example, our TCMT32.52 tools are:

```
T: Triangular
C: 7 degree clearance
M: (within a certain tolerance)
T: (certain type of geometry)
3: 3/8" inscribed circle
2: 
5: 5/32" thick
2: 1/32" corner radius


Interstate Turning Inserts
Shape: 	Triangle
ANSI Number: 	TCMT32.52
Manufacturers Catalog Number: 	TCMT3252
Style: 	TCMT32.52
Insert Style: 	TCMT
Insert Size: 	32.52
Manufacturer's Grade: 	ICP22
Material: 	Ceramic
Inscribed Circle (Decimal Inch): 	0.3750
Inscribed Circle (Inch): 	3/8
Industry Grade: 	C2
Insert Thickness (Decimal Inch): 	0.1560
Insert Thickness (Inch): 	5/32
Corner Radius (Inch): 	1/32
Hole Size (Decimal Inch): 	0.1730
Relief Angle: 	7
Included Angle: 	60
Insert Holding Method: 	Screw-On
```

## Further reading ##
This page gives a good overview of lathe operations for CNC in general and LinuxCNC in particular:

http://www.linuxcnc.org/docs/2.4/html/lathe_lathe-user.html

A short overview of LinuxCNC lathe capability:

http://www.linuxcnc.org/index.php/component/content/article/28-emc2-controls-lathes

Some discussion on advanced features:

http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Lathe_Advanced_Features

A good general machining center discussion, including lathe information.  Gives good coverage of the tool table format.

http://www.linuxcnc.org/docs/2.4/html/common_machining_center.html
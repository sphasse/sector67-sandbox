

# Understanding CNC lathe thread cutting #
## Introduction ##
This document describes gives some background on the Sector67 Sieg CNC lathe and describes a process for cutting threads using that lathe.  Cutting threads on a manual lathe is typcially accomplished by synchronizing the spindle motion with the Z axis motion using a set of "back gears" that engage a lead screw that is used to drive the carriage.  A half nut is used to engage and disengage the carraige, and an indicator is used to ensure multiple thread cutting passes run in the same groove.  CNC lathes typically do not have back gears or a half nut, and the carriage lead screw is controlled with a motor.  As a result, spindle and Z axis motion must be coordinated in software.  A Our CNC lathe has a spindle encoder with an index pulse occuring on each spindle revolution.  We've hooked this encoder into LinuxCNC and as a result our lathe is capable of coordinated spindle/axis motion and thus can cut threads.

## Threads in general ##
Before cutting threads using either a manual or CNC lathe, it is helpful to have an understanding of thread forms in general.  This page:

http://en.wikipedia.org/wiki/Unified_Thread_Standard

provides a good overview.  Some useful terminology:

### The Crest ###
Also called the "flat", is the top or outer surface of the thread joining the two sides.

### The Pitch ###
Is the distance from a given point on one thread to a similar point on a thread next to it, measured parallel to the axis of the cylinder. The pitch in inches is equal to one divided by the number of threads per inch.

### Thread forms ###
The most common thread forms we'll be cutting are ISO Metric and UTS threads.  They both have a 60 degree included angle and a crest that is 0.125 times the pitch. Since we are using a pointed threading tool, the thread depth ends up where it needing to be calcuated from the crest.

## Threads using gcode ##
This section describes the process of threading using the LinuxCNC G76 Threading Cycle command.  More information on that command is available from:

http://linuxcnc.org/docs/html/gcode/gcode.html#sec:G76-Threading-Canned

including good treatment of the various parameters.  I won't duplicate that documentation here, but you should read and understand all of the G76 command parameters.  Some threading considerations are:

  1. I have personally found it most convenient to hand-code the facing/turning code associated with the threading operation and the parameters of the threading operation itself.  This requires a relatively comprehensive understanding of the parameters and their impact on threading.  Unfortunately I am not aware of a script or other software tool that will generate an appropriate G76 code for LinuxCNC, but one would be helpful.  The gcode included below does extract most of the configuration to variables.
  1. I find it conceptually simpler to be in diamter mode (G7) when coding the G76, although radius mode will work as well.  However, when in diameter mode you have to keep in mind that all of the X axis parameters are also diameter mode.  This can be somewhat confusing when considering the initial cut depth (J) and full thread depth (K) parameters.
  1. Some Z axis acceleration is inevitably required when syncing the Z motion with a turning spindle.  You should start your threading operation away from the actual threads a bit so that this acceleration happens outside of the cut threads.
  1. Our carbide thread cutting tool (http://mesatool.com) uses MT-3-TR inserts and is large enough to cut threads 11TPI or smaller.  The insert is 0.093" wide, so you should not thread closer than half of that to a faced edge.

## Sample LinuxCNC gcode script ##
```
(t1 is for facing and right hand turning, t4 is threading tool)
(proper tool offsets should be set in the tool table!)
(touch off the z=0 at the right end to be threaded = coordinate system p1 g54)

#<pitch> = 0.076923 (in threads per unit)
#<major_diam> = 0.50 (the major diameter of the threads)

#<initial_cut_depth> = 0.007 (this will depend on the material)
#<full_thread_depth> = [1.516 * #<pitch>] (might need to adjust this less deep to tighten or more deep to loosen thread fit)

#<stock_diam> = 0.65 (The stock diameter.  Give yourself a little slack here to avoid an aggressive first cut on out of round material)
#<safe_diam> = 1.5 (a diameter at which tool changes can be done)
#<tool_change_diam> = 1.5

#<excess_stock_length> = 0.10 (the distance to the right of Z=0 to starting facing.  Should be evenly divisible by the facing_cut_depth)
#<facing_cut_depth> = 0.01
#<facing_feed_rate> = 5
#<full_facing_depth> = -0.0625 (only used to determine how far to go when facing.)
  (For solid stock, go past the center when facing to account for the tool diameter)
  (For tube stock, specify a depth that will face the tube.

#<length_to_turn> = 0.550 (should be at least 0.050" longer than the length_to_thread to leave room for the threading tool)
#<length_to_thread> = 0.5 (the length to actually cut threads)
#<turning_cut_depth> = 0.01 (how aggressive to cut on the initial turning cuts.  the difference between the stock_diam and the major_diam should be evenly divisible by this)
#<turning_feed_rate> = 5

#<chamfer_side_length> = 0.1 (the size of the chamfer at the right end of the threads, Should be evenly divisible by the facing_cut_depth)
(due to the cutter having a radius and not using cutter compensation, the chamfer will actually be a bit smaller than this setting)

#<turning_rpm> = 800
#<threading_rpm> = 600



g20 (units are inches)
g64 (continuous mode with optional path tolerance)
g18 (XZ plane)
g7 (diameter mode)

T1 M6 (load tool T1, left hand turning)
G43 (apply tool-specific offsets)

M3 S[#<turning_rpm>] (spindle speed)

F[#<facing_feed_rate>] (set the facing feed rate)

(loop to face off the end of the material to Z=0)
G0 X[#<safe_diam>] Z[#<excess_stock_length>] (move to start position)
#<zpos> = [#<excess_stock_length>] (starting facing at the excess_stock_length, face down to z=0)
o101 while [#<zpos> GT 0]
  #<zpos> = [#<zpos> - #<facing_cut_depth>] (new length)
  G0 Z[#<zpos>]
  G0 X[#<stock_diam>]
  G1 X[#<full_facing_depth>]
  G0 Z[#<excess_stock_length>]
  G0 X[#<safe_diam>]
o101 endwhile


F[#<turning_feed_rate>] (set the turning feed rate)

(loop to turn down to the threading diameter)
G0 X[#<stock>] Z[#<excess_stock_length>] (move to start position)
#<xpos> = [#<stock_diam>] (starting turning at the stock_diam, face down to major_diam)
o102 while [#<xpos> GT #<major_diam>]
  #<xpos> = [#<xpos> - #<turning_cut_depth>] (new depth)
  G1 X[#<xpos>]
  G1 Z[0 - #<length_to_turn>]
  G0 X[#<stock_diam>]
  G0 Z[#<excess_stock_length>]
o102 endwhile


(loop to create a chamfer)
G0 X[#<stock_diam>] Z[#<excess_stock_length>] (move to start position)
#<cham_pos> = 0 (keep track of the chamfer cut with this variable)
o103 while [#<cham_pos> LT #<chamfer_side_length>]
  #<cham_pos> = [#<cham_pos> + #<turning_cut_depth>] (new depth)
  G0 Z[0 - [ #<cham_pos> / 2]] (diameter mode is X only)
  G1 X[#<major_diam>]
  G1 X[#<major_diam> - #<cham_pos>] Z0
  G0 Z[#<excess_stock_length>]
  G0 X[#<stock_diam>]
o103 endwhile


g0 X[#<safe_diam>]
T4 M6 (change to the threading tool)
G43 (apply tool-specific offsets)

M3 S[#<threading_rpm>] (spindle speed)


(move to the drive line for the threads)
G0 Z[#<excess_stock_length>]
G0 X[#<stock_diam>]

(run the threading command)
G76 P[#<pitch>] Z[0 - #<length_to_thread>] I[#<major_diam> - #<stock_diam>] J[#<initial_cut_depth>] K[#<full_thread_depth>] Q29 L2 E[#<full_thread_depth> / 4] H4

G0 X[#<safe_diam>] Z[#<excess_stock_length>] (move back to a safe start position)




m5 (stop spindle)
m30 (end program)
```
## TODO: Additional CNC threading tasks ##

The program above will cut good basic threads.  Some additional tasks that should be proven out with demonstration code are:

### Steeper exit angle ###

### Change to metric units and test ###
This should be fairly straightforward but needs to be tested

### Left hand threads ###
This would require:
  * Changing the carbide insert to have a left hand cutting insert (we have several)
  * Changing the start of the drive line to the left side of the threads
  * Changing the thread start to have a tapered entry

### Multiple start (two and three spiral) threads ###
To do multiple start threads, replace the single G76 entry with multiple entries with the pitch being a multiplier of the number of starts and a Z offset of one pitch for each start:

Double start example:
```
(move to the drive line for the threads, first start)
G0 Z[#<excess_stock_length>]
G0 X[#<stock_diam>]

(run the threading command)
G76 P[#<pitch> * 2] Z[0 - #<length_to_thread>] I[#<major_diam> - #<stock_diam>] J[#<initial_cut_depth>] K[#<full_thread_depth>] Q29 L2 E[#<full_thread_depth> / 4] H4

(move to the drive line for the threads, second start)
G0 Z[#<excess_stock_length> + #<pitch>]
G0 X[#<stock_diam>]

(run the threading command)
G76 P[#<pitch> * 2] Z[0 - #<length_to_thread>] I[#<major_diam> - #<stock_diam>] J[#<initial_cut_depth>] K[#<full_thread_depth>] Q29 L2 E[#<full_thread_depth> / 4] H4

G0 X[#<safe_diam>] Z[#<excess_stock_length>] (move back to a safe start position)
```

Triple start:
```
(move to the drive line for the threads, first start)
G0 Z[#<excess_stock_length>]
G0 X[#<stock_diam>]

(run the threading command)
G76 P[#<pitch> * 3] Z[0 - #<length_to_thread>] I[#<major_diam> - #<stock_diam>] J[#<initial_cut_depth>] K[#<full_thread_depth>] Q29 L2 E[#<full_thread_depth> / 4] H4

(move to the drive line for the threads, second start)
G0 Z[#<excess_stock_length> + #<pitch>]
G0 X[#<stock_diam>]

(run the threading command)
G76 P[#<pitch> * 3] Z[0 - #<length_to_thread>] I[#<major_diam> - #<stock_diam>] J[#<initial_cut_depth>] K[#<full_thread_depth>] Q29 L2 E[#<full_thread_depth> / 4] H4

(move to the drive line for the threads, third start)
G0 Z[#<excess_stock_length> + 2 * #<pitch>]
G0 X[#<stock_diam>]

(run the threading command)
G76 P[#<pitch> * 3] Z[0 - #<length_to_thread>] I[#<major_diam> - #<stock_diam>] J[#<initial_cut_depth>] K[#<full_thread_depth>] Q29 L2 E[#<full_thread_depth> / 4] H4


G0 X[#<safe_diam>] Z[#<excess_stock_length>] (move back to a safe start position)


```

### Internal threads ###
We have successfully cut internal threads.  TODO: post the script to do so.

### Pipe threads ###
These will need to be done using G33 rather than G76, so some sample code should be written for it as well that does the proper cleanup and taper.

### Acme threads ###
These would require grinding an Acme form threading insert.

### Measuring threads ###
Accurately measuring the depth of threads can be challenging.  http://littlemachineshop.com/instructions/ThreeWireMethod.pdf describes a method for measuring threads using three wires.
# Introduction #

A build log of the ProjectSheetCake project.



## 8/11/2011: Initial testing of the integration board ##
Scott:

I had some time tonight to finally make earnest progress on testing the integration board.  Chris had allocated a PC for EMC2, and I was able to:

  * Added another prototype perf board to the integration board for the LED indicators
  * Changed one of the standoffs to be plastic as it was hitting a solder bridge.
  * Soldered in wires for the servo enable and servo reset output signals and attached those wires to the screw terminals.
  * Install the PCI card (with 50 pin ribbon cables repurposed from SCSI cables with the active terminators removed) into the EMC2 PC.
  * Boot the PC with an EMC2 live CD and install Ubuntu+EMC2 to the hard drive
  * Confirm via the Synaptic Package Manager that the hostmot2 packages were already installed
  * Run EMC2 (Applications -> CNC -> EMC2) and choose a configuration of (hm2-servo -> 5i23).  I chose to create a desktop icon for this install.
  * Temporarily install the integration board to the mill and hook up the encoder DB9 connectors
  * Confirm that moving the mill manually was reflected properly in EMC2!!!  This means that the encoder wiring through the DB9 ports to the 7i33 daughter card to the 5i23 PCI card is basically correct.  There are a lot of things that could have gone wrong here, but all three axes appear to work correctly, and I even guessed right on the A/B encoder signals :-).
  * Chris and I then attempted to move the Z axis servo via EMC2.  I switched the header from the Anilam board to the integration board, and the Z axes moved properly (although not tuned) with manual commands from EMC2.  Note that the estop and servo enable circuits were still being handled by the Anilam board.  Occasionally got following errors on the Z axis, and it is clearly moving further than EMC2 thinks it is moving, but the basics are there.  Great success!!!
  * Tried the same with X and Y, and had less success.  I moved the X and Y headers to the integration board, and had following errors soon after "machine on" in EMC2 on the X axis without even attempting to move the axis.  The X axis was actually moving when not commanded to.  I'm not sure if this is due to ground differences between the integration board, etc. but that will need to be determined.
  * There was an error in dmesg about too much jitter, and so I ran the jitter test and indeed the machine did not perform well (8,000,000ns+ jitter).

Things that came up tonight as future to-dos:

  * Get a PC with better real time performance
  * Get a PS2 mouse so that we can have both PCs working at the same time using the 2-PC KVM switch.
  * Get an Ethernet connection provisioned to that corner for the 1100m machine so that we can email files, etc.
  * Solder up LED indicator board for the integration board.
  * Try the estop circuit with the integration board

## 8/14/2011: Integration board LED indicators ##
Laura, the boys and I worked on the integration board a bit this evening, soldering up an LED indicator board which will give a visual indication of limit state, estop state, etc.  Luke did a great job soldering and Levi did a great job placing components on the proto board.  Luke does a cleaner job of soldering than I do, and I got to show him how to make a solder bridge on a perforated proto board.

## 8/14/2011: Additional testing of the integration board, EMC2 configuration ##
Good progress made this evening:
  * The integration board hardware is nearly in a complete state.  The LED indicators now fully work
  * I changed the power management settings on the Compaq W6000 PC, and that had a major positive impact on the jitter results, going from > 8,000,000 to < 20,000.  This is great news as it moves the PC from unusable for EMC2 whatsoever, to working very well for both servo and stepper configurations.
  * I used pncconf for the first time and have found this to be a very helpful tool.  The X and Y were switched relative to what I would expect when configuring the axes, as were A and Z.  Other than that (and pushing through setting bogus values for tuning), it generated a working config for the servo controllers (but not IO yet).
  * The servo enable LED was not functioning correctly, and I figured out why.  The input of the relay I was using to indicate servo enabled was at 24V and I was expecting it to be ground until it was energized.  I needed to switch that LED to have +24v supplied from the rail and to get ground when energized.  This LED then worked properly
  * I did my first testing with the entire board (motion and servo enable sides) hooked up.  Anilam complained about not seeing the board, but I was able to get the servos enabled by shorting the servo enable OUT1+ to OUT1- and temporarily shorting the servo reset (OUT3+ to OUT3-) so the integration board circuits themselves seem to be functioning well, I just need to fix:
  * I cannot yet get I/O to work properly.   I'm not sure at what level I'm having a problem; cable, HAL, etc.  I need to learn more about this.
  * The second critical problem I continue to have is following error when the servos should be still.  When I enabled the servos manually by shorting pins, both the X and Z axis appeared (based on the EMC2 display) to be moving tiny fractions of an inch basically continuously.  I'm not sure if this is an encoder or control signal error, some sort of servo tuning needed or some software tuning/compensation, but I need to understand that better as well.
  * TODO: I should switch to powering the EMC2 server from the same outlet as the mill so that I can rule out ground difference problems.
  * Discovered that the HAL manual has decent documentation of halmeter and halscope, so I'll dig into those the next change I get, as they might be useful do debug both the I/O not working issue and the following error when the servos are enabled.
  * One idea I had was to configure the system with 4 servos and 2 steppers, so that eventually if we use some steppers we won't be stepping on the same I/O pins that would be used by the stepper configuration.  This might mean changing the current I/O assignments to the integration board, but in the long run would support running steppers more easily.

Seems like the next tasks with respect to integration of the "custom" Anilam servo reset functionality are:

  * Generate a pyvcp custom panel for servo reset at least
  * And the corresponding HAL configuration for a servo reset pin
  * Integrate it into the axis GUI

## 8/16/2011: I/O working! ##
Scott:

Tonight Luke and I were able to put some finishing touches on the integration board.  Estop input was soldered up, and pcnconf was used to make the input work.  I did indeed have the pins wrong in pncconf as I was using the wrong pin numbers from the 7i37TA data sheet.  I was using the pin number in the output header (1 and 3), and I needed to be using the pin number of the input to the card (35 and 39).  The outputs needed to be inverted, as well as the estop input.  After that, servo enable and servo reset (temporarily configured as spindle ccw so I have a button for it already) worked great.  So, problem #1 is basically solved, and estop in works fine as a bonus.

I moved the PC on top of the controller box as a more convenient location for it.

I still have the problem of the servos not sitting still, though.  In pncconf I believe that proper direction of the table required inverting the servo amp output, but still the servos were not stable.  I plan to send a query to the emc-users mailing list about this to see if anyone else has encountered it.  I want to get the board schematic online first though, so people can understand the integration board.

Some next steps:

  * Test adding an extra widget to the axis GUI using pyVCP to provide a "Servo Reset" button.
  * Email EMC2 users group regarding unstable servos
  * Investigate the spindle head to see how best to control that and start designing a spindle controller interface
  * Figure out the X, Y and Z axis scales so that we have the distances correct.

## 8/17/2011: An afternoon of frustration ##
I was unable to make any headway against the servo stability issue, so I gathered some data and updated my question to the mailing list.  I did work out the encoder count is 1500 and threads per inch on the X axis lead screw is 5.

## 8/17/2011: Basic servo stability, and first gcode run ##
After working through a diagnostic procedure to make sure voltage levels, etc. were all correct, it turns out I was hitting a bug in pncconf 2.4.3 where inverting an axis also caused the max\_output parameter in the ini file to be set negative when it should actually be positive.  Manually changing the max\_output to be positive got the axes relatively stable, and some additional PID tuning got it to the point where I was able to run a gcode program through without problems.

This problem forced me to dig a bit more into the EMC2 internals and as such was a good learning exercise.  I'm glad in the end it wasn't a hardware problem but ultimately a relatively simple software one.

A lot more tuning is needed, including properly calibrating the axes, determine what we can do for acceleration, and many other things, and that will all take some time, but the system is now basically functional as a mill again.

I did realize I had some axes crossed in the integration board, so I rewired those and will be updating the schematic to reflect the change.

I also realized the only reason we needed the in-chassis 5, +/-15V power supply was to drive the LED indicating it is working, so I'll be removing that from the board design, and relying on cable power (per a recommendation from Mesa to prefer that unless the drop is too much) to power the daughter boards.

So, moving forward the next steps for the mill controller are:

  * Get all axes calibrates so that we really know how much we're moving
  * Figure out maximum velocity and acceleration for the axes
  * Add a servo reset custom button (David is working on this)
  * Spend some quality time tuning the axes for real for better and higher performance
  * Set the following error back to a reasonable and safer level
  * Configure the table axes limits properly

I realized that when I calculated the encoder ticks, I was turning the handle one turn, but that was including the gear ratio in the measured value.  That means the numbers from the Anilam configuration now make much more sense.

## 8/23/2011: servo reset automation investigation ##
I was "faking" a servo reset button with the spindle CW output pin, and had the rude realization that if I left servo reset on, if the machine when to a limit switch, when I manually recovered it it would head back into enable mode and potentially start spinning the servos again.  There are really two deficiencies here that combined to make this unsafe behavior:

1) The servo reset out should not be able to be constantly enabled.  Instead, it should either be a momentary enable push button, or it could also be an automatic ~1s pulse on machine on.  David is working on the push button approach with PyVCP, and I have started investigations of the automated solution using ladder logic.

2) When the machine hits a limit switch, it should put the machine into the estop state.  The way the latching circuit works, it will be somewhat complicated to have a single "NO\_FAULT" type signal.  However, an extra input pin could be used to provide the "ALL\_LIMITS\_OK" signal to EMC2, and then hook that up to a ladder program to go to an estop state.  I am somewhat surprised pncconf does not have a ready-made input for limit switches (I have till now told it not to home, etc.), and it is possible it does, so I'll investigate.  It appears I just need to tell pncconf that there are physical limit switches, but no home switches, and then see if it gives me a pin to hook up.  I expect it will.  I'll then need to solder wires to the ALL\_LIMIT\_OK signal, and likely have it inverted in EMC2 to work properly.

Both of these really should be done in the interest of safety.

In addition, I have been curious about adding additional stepper motors to this system, but have noticed that when adding stepgens using pncconf that they are mapped to pins that are not output pins in the isolated I/O card.  According to documentation here:

http://blog.gmane.org/gmane.linux.distributions.emc.devel

This might mean that stepgens are relatively difficult to use with the isolated I/O card (without remapping the cable), and that I should put general purpose I/O on the third connector, and leave connector #2 for stepgens.  Alternatively, I could make a cable that would remap the pins appropriately, but that might be more confusing than it is worth.  I expect that servo drivers take ttl directly and do not need isolated I/O.

## 8/25/2011: a productive night at S67 ##
I spend most of the evening at S67 tonight working on this project.  I made a lot of progress, including:
  * Took the board out and soldered wires for the limit switches and attached them to an input pin
  * Got some pictures of the integration board with my camera phone (forgot a better camera).
  * Re-ordered the 50 pin cables so that custom I/O is using the last 50 pin cable in case we want to use stepgens which automatically get put to specific pins on board 2 that are not compatible with the isolated I/O card.  Looks like I bought one too many isolated I/O cards.  Perhaps if we convert the 3300 mill :-).  The stepper controllers for stepgens would need to take TTL level signals, which should be fine.
  * Upgraded to EMC 2.4.6 via buildbot.linuxcnc.org and confirmed the MAX\_OUTPUT bug is fixed.
  * Measured axis values to determine X, Y, Z scales of 30000, 30000 and 36000.  Output is now scaled correctly, but I'm not sure why that doesn't add up to what Anilam was using for config.
  * Used the new pncconf to re-generate the configuration, fixing following error, max velocity, acceleration, encoder scaling so that the mill is basically a stable mover now and should be basically accurate.
  * Did some investigation of PID tuning, but only preliminary
  * Drilled holes in the back of the integration board for eventual mounting (7/32" holes 8 3/8" apart centered on the board).  Slots might be easier to install, but holes were easier to make.
  * Put numerous generations of the configuration under revision control.
  * Implemented a timed servo reset classic ladder program that seems to work as expected.  This, along with the limit switch addition should make things easier and safer.  It took some debugging to get it integrated via pncconf.  pncconf was not adding custom.hal to the ini file hal entries for some reason, even when seemingly requested to do so.
  * Speaking of which, hooking up an all axis limit switch was easy, and now the machine realizes is has hit a limit switch and stops on its own (in addition to the hardware switches stopping the servos).  The limit switch did not need to be inverted in pncconf, as it is a signal that indicates the limit was hit.
  * Re-ran the EMC2.4AXIS program with a sharpie with the correct scaling.  Looks great, and can't wait to run a real program.

Now to-do:
  * PID tuning as needed for all axis
  * Send an email to the list as to why I am getting consistent following error
  * Try a USB joystick for jogging.
  * Try a relay on the isolated I/O, how to hook this up to custom gcode?
  * Disable ubuntu update to it is not prompting to update packages, which might break EMC2
  * Document most of what I did tonight in earnest
  * Note to the list about pncconf not including HAL ini entries for custom.hal and custom\_postgui.hal (get emc2 version for this)
  * Document the relay board pins in the wiki
  * Document the relay board circuit in KiCad

I probably should start in on the frosting extrusion problem, but in any case probably won't get that done by Aug 31.


## 8/26/2011: some playing with frosting ##
Spent a little time working on this today.  Looks like a USB joystick will be fairly easy to integrate, hooked mine up and was able to fairly quickly get hal pins firing from it.

I also realized on re-reading the EMC2 user's manual that the digital out pin I was using for servo reset is probably intended as the digital out gcode command, so I will need to re-map that, which will be actually clean up the custom hal a tiny bit.

Most significantly, though, Luke and I spent some time fabricating a pressure pot for the frosting, and playing with frosting under pressure.  It seems that 80psi will be sufficient for what we want to do, and putting a pinch valve at the bottom of the pot should be good as well.  The major problem with our version 1 design is that the air pressure tunnels through while there is still a lot of frosting sticking to the sides, and the exiting air tends to be devastating to any frosting already laid down.  I tried a simple floating plunger, but I need to have one with some height so that it does not get sideways, as my initial attempt failed in that way.

I had the additional thought to put a rubber cone on the bottom of the floating plunger such that when it reached the bottom of the cylinder it would seal it.  This would provide an empty cylinder mode of off versus open, which would be greatly superior.

In general, though, the extrusion itself looked fairly reasonable, although I have not done any serious testing.

I need to order solenoids appropriate for the pinch valve and start testing how much force it will take on a relay that is normally closed.  That is, how much will it take to have the fail safe mode close the valves.  I expect I might need to add springs for that, but I am not sure.


## 8/30/2011: joystick jog basically functional ##
I used the very helpful procedures and code here:

http://wiki.linuxcnc.org/emcinfo.pl?Simple_Remote_Pendant

and

http://softsolder.com/2010/10/23/logitech-gamepad-as-emc2-pendant-eagle-schematics-for-the-joggy-thing/

to implement a simple joystick jog.  Luckily, I had the same exact joystick, so all of the input pins matched up.  I had to comment out the fourth axis stuff, as my halui did not have those entries, but other than that, I used pncconf to register (not sure if that is the right terminology) the device.  My understanding of that is that it puts a file in the /etc/udev/rules.d  directory that sets permissions on the joystick device (e.g. /dev/input/js0) such that it can be read by the user.  From there it is a matter of custom\_postgui.hal entries to perform the appropriate logic and mapping of the inputs to the halui jogging functions.

In addition, the following is needed, which I added into the:

```
loadusr -W hal_input -KRAL Logitech
```
Your device name might vary, as it needs to be unique.  I should try literally putting the full ""Logitech Logitech Dual Action" string in double or single quotes to see if that will work.  The hal\_input man page seems to indicate it might.

This seems to be an even simpler and better option worth investigating:

http://wiki.linuxcnc.org/uploads/joypad_v3.hal

As an aside, I am finally starting to get a good sense for hal modules, the ini file, hal files and how they interface with a gui like axis.  I'm also getting a decent sense of what pncconf does for you and what it does not do.  It is a very well thought out and well executed system.

Also a thought:  perhaps I can make a more modular custom\_postgui.hal file using source 

&lt;filename&gt;

.hal commands?


## 8/31/2011: happy birthday and frosting extruder testing ##
More testing today with the frosting extruder.  I will probably want to add a decent pressure regulator to the setup, as running overpressure (~100 psi) caused hose failure issues.  The design is getting refined.  The plunger worked to eliminate tunneling, but a cone on the end did not cause airflow to stop when empty (it was seemingly reduced, though).

A pinch valve run directly from a solenoid is going to be challenging, as the force needed seems quite high.  I am going to try a gate valve rated for 30 PSI and see how that fares.  If well, the design will be quite simple.

## 9/4/2011: more failed frosting tests, digital I/O refinement and steppers ##
I started the day with some frosting testing.  40PSI is definitely enough to push frosting through the 1/4" NPT barbed fittings I have.  Unfortunately, the gas valve Chris loaned me could not shut off the frosting, even close to its rated 30PSI.  So, it's back to the drawing board on that one.

I was able to clean up the extra digital I/O though.  I assigned pins to all 4 digital inputs and outputs, and added a custom servo-reset net and assigned servo reset to that.  All you need to do in pncconf is type a name into one of the pins and it will be added as a custom net.  Not that obvious from the user interface, but handy nonetheless.  I also modularized the custom hal by using the "source" hal command and extra files (e.g. "source servo-reset.hal").  This cleaned up the custom\_postgui.hal quite a bit and should allow me to mix and match features more easily.

The custom\_postgui.hal still is not being added automatically, desipite a custom ladder configuration, and if I configure pncconf to add it via the PyVCP, then EMC2 fails to start with some bad hal entries.  I did not debug this completely, but it seems like a custom ladder program should result in custom\_postgui.hal being added to the ini file.

Finally, I made a lot of progress today on adding a stepper motor as a fourth axis.  I used pncconf in XYZA mode, added one stepgen in addition to the 4 PWMs and encoders, and it assigned pins to a stepgen.  I was especially glad I am using the last 50 pin cable for what will remain "hard-coded" I/O (servo reset, limits, estop), because indeed the stepgen pins were assigned to the second 50 pin cable seemingly without the ability to customize the assignment.

Moving forward, it will make the most sense to have the second 50 pin cable be TTL-level (not opto isolated) interfacing to circuitry for things like stepper motors (I am currently using a pololu A4988 stepper motor driver carrier), additional analog inputs and outputs (via frequency generation, with e.g. an LM331), and additional digital inputs and outputs, isolated as needed.

I have been thinking of a shield format, much like Arduino has, so that additional custom motion control functions could be snapped on and off.  Along with custom emc2 configurations, this would work quite nicely to allow customization of the machine's capabilities.  In the meantime, though, I am just soldering up a one-axis stepper interface card.

I finally did make use of the Anilam +5,+15,-15 power supply.  It is rated for 2 amps on each of the 15V legs, and 6 amps on the 5v leg, so it should easily be able to drive a small stepper via the A4988 driver.  I have the interface board nearly done, I just need a stepper motor for testing hooked to the correct pins.

I also did get a looping gcode program working to run two-dimension tests such as controlling dwell time and z depth for extruding.  Should come in handy if I ever get frosting extrusion working.

To find the pin assignment, I used the output of "dmesg" with the XYZA stepper motor configuration running.

Todo:
  * Fix my soldering defect on the stepper board
  * Get the stepper motor for testing
  * Wire enable to the stepper driver and assign a pin?
  * Jumpers for selecting microstepping?
  * Actually test moving the stepper

## 9/16/2011: a step back for some prioritization ##
I have some time away from this project for my father-in-laws visitation, funeral and burial, which should be a good chance to do some thinking about relative priorities and TODOs moving forward.  Some possibilities:

  * Drill a hole in the case for the 50 pin ribbons so that the box door can be closed during milling.
  * Test voltage loss on a 5' 50 pin cable to see if we could put the PC in the cabinet on the other side of the mill and still use ribbon-supplied 5V.
  * Test the stepper driver chip+circuit+motor w an Arduino while away from S67
  * Solder stepper card enable, MS0,1,2 do digital IO (digital IO to spare, makes microstepping rate software-controlled)
  * Determine wiring/interface standard for digital and analog I/O to arbitrary mill accessories (banana plugs?)
  * Get the probe assigned as a pin
  * Get a spindle encoder installed and wired up
  * Get the spindle speed and direction control wired up as the 4th axis.
  * Get the spindle enable and brake wired up for safety.
  * Wire the manual spindle controls into EMC2, and then configure EMC2 to allow manual or automatic spindle control (in theory the best of both worlds, but not easily reversible if we want to go back to the Anilam control
  * Sample frequency=>voltage and voltage=>frequency circuits with LM311 chips and the software config (encoder and PWMgen) for them
  * Document the servo reset circuit for the wiki
  * Finish other misc TODOs currently on the wiki page
  * Update to EMC 2.5 when available/stable for coordinated analog motion
  * Investigate the relatively high following error and resolve
  * Complete PID tuning of each axis
  * Learn how to interface custom components properly with axis and halgui
  * Test the frosting servo using a 12V supply
  * PVC pressure vessel?
  * Design and fabricate a frostruding cake tip adapter
  * Understand how to cut pipe threads on a lathe with no taper

Whew, OK there is plenty to work on in that list.

## 9/26/2011: re-visiting PID tuning ##
Found this link that provides a seemingly reasonable procedure:

http://www.newport.com/servicesupport/Tutorials/default.aspx?id=152

## 10/18/2011: Spindle VFD drive troubleshooting ##
For posterity, I manually modified the ini files to set the axis ranges plus and minus their extents, so after homing you can still move the Z axis in the positive direction.  I'll need to make that change the next time I generate via pncconf.

Finally getting back to this project and wanting to mill some stuff.  The spindle VFD drive has been acting up (Compumotor DriveBlok that came with our HH Roberts spindle head).  We get a DC under voltage condition (5 red LED flashes).  We took the capacitor portion of the DC supply off (the "Cap Blok") and it seems to be OK, but we can't be sure.  We had some fits getting RS-485 communications working to the drive, but now basically have things functional.  Problems included:

1) Use of a null model serial cable instead of a straight through cable.
2) Potentially bad RS232-RS485 converter or dead batteries in the converter.
3) Send and receive wires needed to be reversed from the diagram.
4) Not knowing the device address ("1") or the default/configured serial port values (9600-8-N-1 no flow control).

Now we are able to send commands and receive error messages, so we seemingly need to work out the checksum calculations or get an RS485 client.

At that point we can perhaps get better diagnostics.


## 11/17/2011: Fourth axis progress ##
Lots has happened since the last update, including significant progress understanding and integrating the [VFD drive](1100SpindleBlok.md).  With a little classic ladder integration, spindle drive faults now estop the mill.

I had an exciting win of the Madison SOUP idea contest to net $180 toward the 4th axis project.

Additionally, the smaller servo drives are now well understood, and the [encoders and signals](FourthServoAxis.md) have been integrated in a very basic way.  The main challenges were that the encoders were differential not TTL and the supply voltage and operation mode for the servo amps was not known.  The 4th axis is now basically ready for integration into hardware.
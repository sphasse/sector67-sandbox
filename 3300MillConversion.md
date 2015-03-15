# 3300 mill conversion #



# Introduction #

After the successful [conversion](ProjectSheetCake.md) of our 1100 mill to EMC2 at [Sector67](http://sector67.org) (and integration of a [fourth-axis rotary table](FourthStepperAxis.md)), we are now tackling a conversion of our exsiting Anilam 3300 mill to EMC2 as well.  This page documents that effort.

# Sponsorship #
This conversion project has been sponsored by [Comprehensive Computer Consulting](http://compcc.com).

In addition, this project would not be possible without significant volunteer effort from members of Sector67 and attendees of the EMC2 integrator's class, which used this project for various laboratory exercises.

# Conversion details #


## Overall integration strategy ##
Efficiently converting the control system of a machine like this requires determining where to "cut the cord" between the existing control system and the new one.  In our case we wanted to preserve the existing motor amps, power supplies, limit switches, estops, etc. but replace the proprietary control system with an open one.  There were basically two reasonable choices for this:

A) Replace the existing DSP board and integrate with the existing relay board.  The DSP board was already receiving and sending all of the appropriate encoder and estop signals and generating servo control voltages.  Somewhat complicating things is that some of the communication between the DSP board and the relay board (presumably for communicating limit state amongst other tings) was done via a CAN bus.  As there is no built-in CAN bus support in Linux CNC we would have to acquire CAN bus integration hardware and write the appropriate LinuxCNC components.  Probably not too daunting, but certainly more complex than hooking up wires.

B) Replace the existing DSP board and relay board.  This would require creation of a new limit/relay board.

Our choice after some discussion was to use approach B) and tackle replacement of the both the DSP board and the existing integration/relay board.  This would require us to make our own integration board, but would leave us in essence with no "magic" proprietary boards that we did not understand.  From a hackerspace perspective, in the end we'll have a better understanding of the hardware and better ability to maintain, enhance and repair it.

In addition, this let us avoid implementing CAN bus integration and in general simplified the overall system.  Since the LinuxCNC software is appropriately sophisticated and extensible, we really lost no functionality with this choice.

This approach is somewhat different that what we took for the 1100 conversion, as the relay board in that case was simpler and easily integrated by simple wiring.  If we take on a more aggressive migration of the 1100 mill, we could replace the servo board as well using the same technique and limit/relay board layout used on the 3300 mill.

In retrospect the decision to replace the Anilam integration/relay board has been a good one, with the combination of a low-cost relay board, a small custom PCB and the Mesa 7i33 and 7i37 boards providing excellent replacement functionality.

## Bill of materials ##
We used the following components

| **Component** | **Source** | **Part #** | **Cost** |
|:--------------|:-----------|:-----------|:---------|
| Mesa 5i23 anything I/O PCI card | mesanet.com |  |  |
| Mesa 7i23TA quad analog servo interface daughter card | mesanet.com |  |  |
| Mesa 7i37TA isolated anything I/O adapter | mesanet.com |  |  |
| 24V 4-relay board | ebay.com | $12.00 |  |  |

and for the custom limit/estop board

| **Component** | **Source** | **Part #** | **Count** | **Total Cost** |
|:--------------|:-----------|:-----------|:----------|:---------------|
| 2x3" perf board | digikey.com                 |  | 1   |  |
| 10 segment DIP LED | digikey.com              |  | 1   |  |
| 1/2W 2.2k resistor | digikey.com              |  | 6   |  |
| 0.2" 3 position pitch screw terminal header |  |  | 4   |  |
| 0.1" 6 position screw terminal header       |  |  | 1   |  |
| 4-40 1/4" male/female aluminum standoffs    | digikey.com |  | ~40 |  |
| 4-40 nuts and bolts                         | digikey.com |  | ~40 |  |
| wire                                        |  |  | about 4' | NA |
| crimp terminals                             |  |  |     |  |

## Integrating the encoders ##
The first step we took on was to integrate the encoder signals.  The encoders are TTL level quadrature with an index signal.  The Mesa 7i23 board makes it very easy to integrate the encoders.  We had to trace down the encoder wires from each axis, cut the wires and wire them up to the appropriate screw terminal on the 7i23.  There were 6-pin Molex connectors on these terminals, and so you could make them pluggable if you wanted but since the 7i32TA has pluggable screw terminals in any case there was really no benefit for us to do this.

The +5V/GND for the encoders was supplied via a separate set of wires, so those were also located, cut and wired to the appropriate 7i23 screw terminals.

With encoder power supplied from the 7i23, we were able to safely verify proper encoder function without powering the mill.

## Integrating the servo control signals ##
We did strip the wires a few inches back and wire the shields together via a p clamp to the star ground.  This should be better from a noise and ground loop perspective than wiring the shields to the ground on the 7i23.

## Integrating estop, limit and servo enable ##


## Understanding the Anilam servo amplifiers ##

The servo amplifiers in both of our mills are Anilam brand servo (one is Accu-rite brand) amplfiers with part number SMA7215-200-1 .  These are manufactured by by Glentek, and the manual is availble from http://todo:get after a free resgistration on their site.  The manual contains a nice introduction to DC brushed servo control and describes the amplifiers in detail.

We are running these servo amps in a velocity mode control loop, with tachometer feedback coming from each motor.

### Motor control DC voltage power supply and relay ###
The manual proscribes a solid state relay for the DC power supply, and we have moved to a mechanical relay instead.  The previous control boad did have a solid state relay.  I don't expect this will have a significant impact on the operations of the amps, and the reason for the recommendation is not given.  Consulting with some motor control folks has left me relatively confident that we won't weld the contacts of our relays, which would otherwise be one reason to use a solid state relay.  NOTE: this confidence was misplaced, perhaps due to our use of cheaper relays.  On one malfunction, the relays welded, and so now we have an SSR in place for the servo DC power supply.

### Amplifier inhibit ###
The wires labled "inhibit" on the Anilam control board are wired to the "clamp" input of the amplifier.  The clamp signal is appropriate for estop, as it brakes the motors for a short time before disbling the amplifier.  This should make things stop on a dime on when estopped, and indeed we did notice some drift in the motors on an estop with the "fault" wires just floating.  Depending on how various DIP switches are set, the polarity of this signal can be configured.  TODO: describe how we configured the correct polarity and wired it to the enable signal of the daughter board.

From the Mesa servo control daughter board data sheet, the servo enable signal is described as TODO: get this...

### Amplifier logic voltage ###
The amplifiers were configured for 15V logic control.  Since the enable signal of our servo control daughter board is TTL level voltage, we needed to reconfigure the logic control to be +5 volts.  TODO: describe how this is done... This, along with the clamp changes from the section above technically change the model number of this servo amplifier to TODO: figure out the new part number based on the manual.

### Tuning the amplifiers ###
The manual gives a specific procedure for tuning the amplifiers out of the box.  In general we can probably assume that the amps are relatively well tuned with respect to the servo drives, but we can record the existing settings and put a scope on the motor output to see if the signals are appropriately tuned.  TODO: do this and record the output.  Additionally, we have noticed a small amount of drift in the amps that can be easily tuned out by adjusting the BAL (balance) pot.

TODO: record the resistance levels on the pots per the manual for each amp.

#### X axis ####

| **Pot**                                                  | **Resistance** |
|:---------------------------------------------------------|:---------------|
| Signal Gain pot wiper (RV7) at J2-5 to common (ohms)   |  |
| Signal Gain pot wiper (RV9) at J2-6 to common (ohms)   |  |
| Signal Gain pot wiper (RV10) at J2-7 to common (ohms)  |  |
| Signal Gain pot wiper (RV13) at TP1-K to common (ohms) |  |

| **Dip-switch** | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|:---------------|:--|:--|:--|:--|:--|:--|:--|:--|:--|:---|
| S1           |   |   |   |   |   |   |   |   |   |    |

| Date data taken:   |       |
|:-------------------|:------|
| Serial number S/N: |       |
| Model number:      |SMA7215|

#### Y axis ####

| **Pot**                                                  | **Resistance** |
|:---------------------------------------------------------|:---------------|
| Signal Gain pot wiper (RV7) at J2-5 to common (ohms)   |  |
| Signal Gain pot wiper (RV9) at J2-6 to common (ohms)   |  |
| Signal Gain pot wiper (RV10) at J2-7 to common (ohms)  |  |
| Signal Gain pot wiper (RV13) at TP1-K to common (ohms) |  |

| **Dip-switch** | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|:---------------|:--|:--|:--|:--|:--|:--|:--|:--|:--|:---|
| S1           |   |   |   |   |   |   |   |   |   |    |

| Date data taken:   |       |
|:-------------------|:------|
| Serial number S/N: |       |
| Model number:      |SMA7215|

#### Z axis ####

| **Pot**                                                  | **Resistance** |
|:---------------------------------------------------------|:---------------|
| Signal Gain pot wiper (RV7) at J2-5 to common (ohms)   |  |
| Signal Gain pot wiper (RV9) at J2-6 to common (ohms)   |  |
| Signal Gain pot wiper (RV10) at J2-7 to common (ohms)  |  |
| Signal Gain pot wiper (RV13) at TP1-K to common (ohms) |  |

| **Dip-switch** | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|:---------------|:--|:--|:--|:--|:--|:--|:--|:--|:--|:---|
| S1           |   |   |   |   |   |   |   |   |   |    |

| Date data taken:   |       |
|:-------------------|:------|
| Serial number S/N: |       |
| Model number:      |SMA7215|


### Integrating servo clamping on disable ###
Ideally we want the motors to briefly brake as they stop in an estop state.  The clamp function enables them to do so.  This is labeled as "inhibit" on the existing Anilam board, and so we want to integrate that clamp function into the Mesa 7i23 servo enable output pin.  This requires some reconfiguration of the Glentek amps, as they are by default configured for +15V logic and the clamp input is configured pull-up, active low.

The Mesa 7i23 describes the enable functions as:

ENABLE INPUT
Each 7i33 channel has an active low TTL level input.  When this input is high, the corresponding AOUT is forced to 0V regardless of the state of the PWM and direciton inputs.  A pullup resistor keeps the enable high if the controller connection is lost

ENABLE OUTPUT
Each 7I33 channel has a 5V CMOS active high enable output available on the SERVO AMP/ENCODER connector.  These signals are the logical inversion of the enable inputs.


The Glentek amps describe their input types like so on page 20 of the manual:

Type "A": Requires grounding of the input to disable the amplifier (pull-up, active-low)
Type "B": Requires a postive voltage at the input to disable the amplifier (pull=down, active-high)
Type "C": Requires grounding of input to enable the amplifier (pull-up, active-high)
Type "D": Requries a positive voltage at the input to enable the amplifier (pull-down, active-low)

Looking at both descriptions, it seems that we want the clamp input to be type "D".

Additionally, we would want the logic level to be +5V, rather than the default +15V.

Leaving the rest of the switches in the default mode, we have the following changes:

| **S1-1** | **OFF** (change to 5V logic) |
|:---------|:-----------------------------|
| S1-2 | OFF |
| **S1-3** | **ON** (change clamp input to pull-up) |
| S1-4 | ON |
| S1-5 | ON |
| S1-6 | NA |
| S1-7 | ON |
| S1-8 | OFF |
| S1-9 | ON |
| S1-10 | OFF |

The limit and clamp share S1-7 and thankfully for our desired configuration both should be ON.

This would in effect change the model number (which informatin on how the switches are configured) to: SMA7215-282 TODO: confirm

NOTE: after doing this for one axis, the servo tripped the 20A circuit breaker and welded the mechanical relay.

# TODOs #
Individual TODOs are listed in the build log per day.

# Build Log #
## 2/9/2012 ##

We made great progress last night during the first session of the mill conversion hackathon.  Scott S dis a great job cleaning out the workspace around the mill control box, and then got straight to work identifying and converting the quadrature TTL-level encoder signals coming from the motors and the +5/GND supply needed to drive the encoders.  Once the X axis was wired to the Mesa servo daughter card we were able build a sample starting configuration using pncconf and see correct movement in the open loop configuration for the axis.

Scott H pulled down LinuxCNC 2.4.7 from the repository to avoid some pncconf bugs.

Brett U and Larry W provided technical assistance confirming proper operation of the encoder signals.  In the mean time Scott H worked on the design and soldering of the I/O integration board, which is the circuit board to integrate LinuxCNC and the relays with the limit and estop switches.

After the encoders for all three axes were wired and confirmed functional, we took a breather to re-group, and then tackled getting the motors to move under LinuxCNC control.  We re-used the existing Anilam servo enable functions to enable power to the drive (rather than hard-coding power, which would take away estop and limit safety).

We tested each axis individually under open loop control to determine which of them needed to be inverted.  After confirming open loop control, we then enabled basic PID control and started a full-blown LinuxCNC instance.  By the end of the session, we had three-axis coordinated motion working.  Some minor problems:

  * Following error needed to be tweaked higher by default.  We need to go back and revisit the PID tuning to resolve this.

  * I had "worked ahead" and defined I/O pins for limits and estop, but since we did not have that board, the maching would not enable (it thought it was on a limit switch), so they had to be removed from the software configuration.

Work we will hopefully accomplish on Sunday 2/12/2012 (noon-5):

  * Fix the shielding on the incoming encoder cables.  This should go to case ground, not ground on the servo card.  We'll want to put a P clamp over the bundle of incoming shielded cables and run that to the star ground.
  * Test the new I/O integration board out of the mill.
  * Implement the I/O integration board in the mill.
  * Remove the existing I/O integration board and extraneous power supplies.
  * Drill mounting holes in the new I/O integration board to match the existing mounting screws
  * Figure out of the servo inhibit wires are going to cause us a problem.  This would be easiest if we can find a data sheet for the servo amps.
  * Wire and confirm the fans are working (check to see if one fan comes on with servo enable and one runs all the time)
  * Install the new monitor, keyboard and mouse on the PC arm
  * Secure the monitor, keyboard and mouse wiring to the arm
  * Wire the ethernet cord to the ceiling
  * Remove the existing large cable PC plug
  * Make longer 50 pin twisted cables and route them through the former large cable plug hole.
  * Create and integrate the servo reset pulse circuit (can copy from the 1100 mill)
  * Make some chips using LinuxCNC!

## 2/12/2012 ##
Another 5 solid hours of build work on the 3300 mill.  Larry W and Scott H got the I/O integration board debugged, tested externally, integrated into LinuxCNC and finally integrated into the overall mill.  With a few minor debugging tangents, it worked exactly as planned.  The integration board, when soldered properly (ha!) works as expected, and, copying the classic ladder 2 second servo reset pulse generator from the 1100 mill we were able to get machine enable working from LinuxCNC.

This is all great news, and after getting the mill working we were able to remove the existing Anilam integration board and 5 and 15V power supplies.  We ran out of time and ended up leaving the machine mid-operation, with some components and wiring still yet to remove and some yet to clean up properly.  The TODOs are:

  * Determine where the PC will ultimately live
  * Make longer 50-pin ribbon cables
  * Remove the large cable plug and all wires hooked to it
  * Wire the internal 24V power supply to the integration board instead of our bench supply.
  * Wire the 120V fans to power (crimp terminals to them)
  * Wire the 24V power supply to power (same crimp terminals)
  * Fix the shield grounding to the case not the servo board.
  * Integrate a 3-phase contactor to enable estop
  * Integrate the oiler power per Chris' request
  * Integrate the inhibit wires into the clamp function (may require reconfiguring the servo amps for 5V logic, confirming the polarity of the signal is correct and wiring each amp to the enable pin on the servo daughter card.


It turns out that if the servo inhibit wires are left to float that they do not inhibit the drivers, although we were not able to find any data sheets for the Anilam servo amplifiers.

We also switched the integration circuit to use the normally open contact on the estop buttons for communicating estop to LinuxCNC.  Although this is workable, it is not ideal, as when the machine is off it shows up as not estopped (but on the limit switches).  This can be a bit confusing and counter-intuitive, and better would be for it to show up as estopped.

For safety purposes we wired a temporary box to hold the estop button using a 120V wall enclosure.  Hopefully this will remain temporary.

## 02/16/2012 ##
Third night of the mill hackathon.  We again made good progress and are within striking distance of having this project mostly wrapped up.  Scott S was there for the first half, making a longer 50-pin ribbon cable with twisted pairs to connect the Mesa 7i33 servo daughter card to the Mesa 5i23 board.  Scott H spent the rest of the night cleaning up wiring, including removing the large cable that used to connect the upper PC cabinet to the servo amp cabinet.

Scott H wired the encoder and servo signal shield wires to the star ground using a P clamp across the shielding.  This is better than running it to a ground in the servo daughter card.  He also

Peter N worked to figure out the 240V contactors, soldered longer leads onto existing 24V power supply, secured ethernet wiring and was generally helpful in the migration.

The wires in the cabinet were again routed through the conduits and by the end of the night things were looking fairly tidy and still functioning properly.

Still to do:
  * Figure out how to energize the contactors and wire that properly (enable only not forward/reverse)
  * Wire the three phase in and out so that the spindle power is not a separate breaker switch (this is a Chris task)
  * Configure the servo amps for proper inhibit/clamp from the Mesa board.
  * Record the existing servo tuning parameters (pots)
  * Wire the inhibit/clamp to the servo daughter board and test
  * Install conduit in the hole previously used for the large signal cable
  * Route the 50 pin cables through that hole to the PC
  * Run the amps in open loop mode and adjust the balance on the axes that move
  * Put the door back on the amp cabinet

If we get all that done, we can integrate the 4th stepper axis:
  * Mount the 36V power supply, wiring it to enabled power
  * Mount the stepper driver
  * Mount and wire a fan for the stepper driver (24V or 120V?)
  * Mount the 5-pin XLR connector to the outside of the case through an existing through hole
  * Wire the stepper drive to the power supply and 5-pin XLR connector
  * Run a minimal ribbon wire from the PC to the stepper controller (+5V, step, direction)
  * Configure LinuxCNC for the 4th rotary axis


## 02/17/2012 ##
Fourth night of the mill hackathon.  A somewhat frustrating and long night.  Thanks much to Brett U and Peter N who worked toward getting the fourth stepper axis working.

We ran into our first real problems tonight.  After wiring up the inhibit on the X axis for what I though would properly inhibit integrated with the Mesa 7i23, I powered the servos and tripped a breaker.  Setting the DIP switches back to stock and unwiring the clamp wire let things start up, but I had actually welded the relay powering the large DC power supply, so the servos were enabled all the time.  obviously not a good situation.

The servo amp datasheet specifies a solid state relay, and now I think I know why anyway.  After switching the relay board (thank goodness we had a spare, it appeared to weld the relay once again on normal powerup, after which it functioned properly but the amps remained powered.  WithY and Z only this did not happen, but with X and Z it did seem to happen but after I heard a click from the relay and it did power down, it was just greatly delayed (like more than a minute).

> Note: I now think this problem was caused by a basic mistake, a ground differential between the 5/15V power supply on-board the servo amp and the Mesa card.  I am still somewhat amazed everything works, and I can't tell where that 20A went that tripped the breaker, but so far things seem properly functional.  Using the isolated I/O adapter I should be able to handle the clamp signal properly.

After lamenting this state of affairs somewhat, I decided to integrate a solid state relay instead, and wired that to the 24V enable.  Some amount of wrangling later and it was working by about midnight, with a wiring cleanup going to be necessary before integrating the stepper power supply.


However, it is in a good enough state now to run for basic testing.  My plan is to route the 50-pin cables through the outgoing air filter for now (this didn't work out as there is a grill, but routing them through the former hole for the PC connection cable did work.)

More work accomplished:

  * 36V stepper power supply mounted
  * mounting bolts for the SSR and stepper amp installed (required unmounting the case for a bit)
  * SSR relay installed and wired temporarily
  * inital work to solder the XLR end onto the servo motor
  * Documented one of the amp's resistance values per the data sheet
  * Monitor clamped to the board

## 02/18/2012 ##
A bit of work this morning to get things ready for "beta test" mode:

  * The estop button mounted and wired more permanently
  * The 50-pin cables all routed through the back of the cabinet
  * The cabinet door back on (although not grounded yet) and locked closed.
  * PC wires routed and zip tied.

In this configuration, with the SSR, etc. the machine is basically functional.

I've reviewed the data sheet for enabling the limit switches and cannot find where I might have gone wrong.  Fixing the clamp circuit will require more in-depth analysis.  The most likely fault IMO is ground differential between the DC power supply and the servo amps.  This theory should be testable.

## 02/21/2012 ##
Further work tonight to integrate the 4th stepper axis:

  * Wired up the machine-enabled-only 120V to the 36VDC power supply
  * Cleaned up the 120V wiring to the main servo DC power supply
  * Soldered the 5-pin XLR connector to both the stepper motor
  * Soldered wires to the 5-pin XLR receptacle
  * Punched a hole in the case for the XLR receptacle and mounted it
  * Mounted the stepper driver, had some problems with this as the screws I mounted in the chassis are too close together to fit a bolt on :-).  So instead I temporarily screwed through the case.  I can hopefully move the right screw hole over a bit to fix this.
  * Wired the
  * Changed the CMOS battery in the PC so it should boot without errors now (thanks Peter N for work on this)
  * Added the "second" 50-pin ribbon cable to the 5i23 card and hooked the 50-pin breakout board with stepper signals to the signal port of the stepper amp.
  * Integrated the A axis into a new LinuxCNC configuration and tested it.  Worked perfectly the first time!

Still need to:
  * Mount a fan on the stepper amp (24V machine on only could be easily routed from the SSR
  * Make a permanent cable for the stepper signal and route it properly
  * Order 6' or 7' cables from mesa for the rest of the 50-pin connectors
  * Get an 1 1/2" conduit connectors and mount it in the box
  * Mount a switch for manual/auto spindle operation and wire 120V enabled for manual mode, versus machine-on-only for auto mode.
  * Clean up the 24V wiring to the SSR, could do this in conjunction with the fan power.
  * Machine the adapter plate so we can mount the smaller three-jaw chuck in the rotary axis
  * Get the servo clamp working with isolated I/O.  This will likely require adding a ground wire coming from each amp.

All-in-all a solid night of progress with visible results.

## 02/26/2012 ##
Sunday cleanup, some relay frustration.

I worked most of the day today on cleaning up wiring and wrapping up some other conversion tasks.  Tasks completed include:

  * Finding a 24V fan for the stepper amp and wiring it in place
  * Stranding the 6' 50 pin cable from Mesa for the I/O and shielding it with metal tape
  * Switching from the 50-pin breakout board to dedicated wiring for the stepper amp control signals
  * Implementing a 50-pin cable with about 10 wires run for the stepper amp control signals
  * Routing all of that signal wire through a plastic shield through the larger hole in the case
  * Heat shrink tubing on the XLR stepper connector
  * Wiring in a manual/auto spindle contactor control switch so that when the spindle power is eventually wired through the case, we'll have the ability to run the mill in manual mode.
  * Took some pictures of the box for documentation
  * Replace the blown 10A SSR with the 25A Anilam board SSR (See IMPORTANT NOTE #1 below)

The remaining task list is finally growing somwehwat shorter:
  * Properly PID tune the servo amps, including max acceleration and velocity.
  * Consider tuning the balance on the servo amps to be neutral.  Currently the X axis at least floats some.  The other axes probably float a bit as well.  This should make the mills a touch less jittery.
  * Implement the clamp signal when the machine is not on (see important note #2 below).
  * Consider a third spindle option (auto, manual, off), or we can just continue to use the breaker switch on the VFD box.

> IMPORTANT NOTE #1: The 10 amp SSR was blown, again compromising estop behavior.  We finally did the smart thing and looked at the rating of the SSR on the existing Anilam board and it was 25A.  So we were basically putting 10A relay devices (at first a mechanical relay that welded, and second a SSR relay that blew) where 25A was needed.  We're currently using the Anilam SSR relay and we'll see how far that gets us.  In theory that should work completely fine, so if we have problems then we know we've got some other issue.

> The thinking there is that when the capacitor on the large DC power supply is completely uncharged it will draw lots of current on startup.  After charging up it'll draw a lot less.  Thus the need for the higher current rating.  I'll need to talk with some power supply folks to confirm this thinking.


> IMPORTANT NOTE #2: When working to understand the clamp signal, I temporarily attached a 0.1" pin header to the ground pin of the test header.  I could then enable the clamping function by grounding the clamp wire to this wire.  Unfortunately, after ungrounding it (removing the clamp function) the servo motor started to oscillate.  I believe this is due to a combination of things:

  1. The servos not being properly PID tuned so that oscillation when under control does not dampen.  Currently they are a naive P-only tuning.
> 2) The following error being set to 1 inch so that the oscillation was allowed to continue.
> 3) The clamping function itself moving the servos a bit so that a non-linear correction needed to be applied when motion was restored.

> This will take some further investigation about how to best resolve it.  Proper PID tuning and tighter following error tolerances are logical next steps for this mill in any case.
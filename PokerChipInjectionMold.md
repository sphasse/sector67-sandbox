

# Introduction #
Sector67 recently acquired an Arburg pneumatic plastic injection molder.  While it came with some test molds, nearly all were at the very limit of the shot size for the molder.  We wanted a more practical mold to demonstrate the machine and so we created a mold for our poker chip.  The machine will run semi-automated and we we ended up creating a quarter of a bucket of chips before having (solvable) mold problems.  This document describes the process of designing, machining and assembling the mold for the machine.

It is worth noting that if you at all value your time there are much more efficient and effective ways of obtaining both molds and molded parts.  Also I am neither an expert machinist nor injection mold designer so this was a largely "seat of my pants" effort that was a major time and effort commitment for a low quality mold.  Frankly I was surprised that the first effort worked at all.  Feedback is certainly welcome.  Caveat emptor and all that.  If you need professional results you should pay a professional.

# Details #
## Mold frame details ##
Our Arburg molder came with a (seemingly after market) Master Unit Die (MUD) quick change frame.  This frame will take a single DF Quick-Change DH-Style insert mold.  Mold blanks can still be [purchased](https://na.dmecompany.com/Catalog/CatalogListing.aspx?CatalogId=DME&CatalogDetailId=333&NSM=Y), but were prohibitively expensive for our application, and as a proof of concept we were interested to machine one from scratch in any case.  As you can imagine, the dimensions of the mold are critical and are documented in the catalog, but we have also created a CamBam file with an example mold including machining steps to provide a quick start.

## Mold digital design ##

![https://raw.githubusercontent.com/sphasse/sector67-sandbox/master/Sector67ChipMold/poker-chip-cambam2.png](https://raw.githubusercontent.com/sphasse/sector67-sandbox/master/Sector67ChipMold/poker-chip-cambam2.png)

All of the design for both the chip and the mold itself was done in using [CamBam](http://www.cambam.info/).  CamBam is an great and simple CAM tool that we use extensively for 2.5D CAM operations.  It is also a sufficient enough CAD tool to lay out the poker chip mold, which is certainly not a trivial design.

Much of the work in the design was determining appropriate tooling, operation order, and speeds and feeds to machine the part.  The mold itself ended up being an 11 step machining operation.

The files for the poker chip mold and ejector plates can be found at https://code.google.com/p/sector67-sandbox/source/browse/trunk/Sector67ChipMold/

## Mold machining ##
This section describes the machining process to help give a sense for what is required when machining a part like this.

Machining notes for the Sector67 poker chip injection Master Unit Die Solid DF Quick-Change mold
### General Information ###
The mold plate measurements are from the Master Unit Die catalog for a 3.25 x 3.15 Solid DF Quick-Change DH-Style Frame:
http://www.dme.net/catalog/DME/MUD%20Catalog/index.html#84/z
The alignment pin inserts are press-fit drill bushings 0.251 ID and 13/32” OD ½” long:
http://www.mcmaster.com/#8491a115/=thryp1
The alignment pins are 1.5” L 0.25” diameter dowel pins:
(TODO: check order)
The ejector pins are from McMaster-Carr:
(TODO: check order)

The machining operations expect a 1.5” thick aluminum blank at least 10” wide and 7” deep with a machineable area at least 9” wide by 6” deep.  Some drill operations and the final machining operation are through the part, so some hold-off from the bed is needed.

### Step 1: Initial facing ###
This operation takes material off 0.75” around what will be the machined part.  The lower left corner of the main part is [X=0,Y=0], so this operation will mill to [X=-0.75, Y=-0.75].  You need to be mindful of that when zeroing X and Y and fixturing.  To touch off X and Y, you can put locate the cutter at the lower left of the cuttable surface and touch that off as X=-0.44,Y=-0.44.  Z=0 is defined as the unmachined top of the blank.  Z=0 still needs to be defined accurately though since the depth of the part is cut down from this offset.  The compressed air blast cooling seems sufficient but this and the following steps make a lot of chips so you should work to keep everything clear.

Tool: 5/8” two-flute cutter

Speed: rough 7ipm, finish 12ipm

RPM: 3000

### Step 2: Chip body ###
This operation mills two circles for the poker chip body.  Z=0 is defined as the faced surface from step 1.  The operation has both a spiral lead in and a spiral lead out to prevent leaving machining artifacts.

Tool: ¼” cutter with 7 degree draft.

Speed: 3.5 ipm

RPM: 3000

### Step 3: Gear detail ###
This operation mills the details of the outside gear and the sector67 detail.  Z=0 is defined as the faced surface from step 1.  Getting the tool Z defined properly is very important since a small different in tool Z could cause the cutter to cut too deep on the first pass and break.  To mitigate this risk, the program starts cutting above what should be the bottom of the machined chip body, so it is expected that one or more passes may cut air.  Keep the chips cleared well during this operation.

Tool: 1/32” cutter

Speed: 4ipm

RPM: 5000 or higher

If we could change the safe height this operation would run much faster, but it would take some investigation to determine if that can be done safely.

### Step 4: Texture drill ###
This step drills the tiny texture holes around the edge of the chip.  Z=0 is defined as the faced surface from step 1.  Again defining this Z height properly is critical to tool health.

Tool: A 0.025” cutter or an engraving blade with a sharp point.

RPM: 5000

As it is difficult to get the Z touch off very precise, after this operation you should check the detail to ensure it is appropriate and if not adjust the touch off or knee to mill deeper.

### Step 5: Sprue and vent ###
As noted below it would be better to do this step after the ejector pins.  This step cuts the sprue and vent.  Z=0 is defined as the faced surface from step 1.

Tool: A 1/8” ball nose cutter.

RPM: 5000

### Step 6: Ejector pins ###
This program needs to be manually edited after being generated from CamBam to have M0 pause commands after each drill operation.  The actual gcode does not drill the holes.  Instead, the program should move to the drill position and then pause, allowing you to use the knee to actually drill the hole.  You can run the program multiple times, once for each drill/reamer.  These holes should be started with a center drill, step drilled fully through to 11/64” diameter and then reamed with a chucking reamer to 3/16” (0.188", 4.787mm).  When using the chucking reamer use a slower RPM but faster feed, and make sure the hole is cleared of chips before reaming.  Z=0 is defined as the faced surface from step 1.

RPM: Appropriate for the various drills/reamer

Tool: various drills including a center drill, 11/64” drills (and smaller steps to that) and 0.188” chucking reamer

### Step 7: Drill alignment holes ###
This step drills holes on both parts for the alignment pins.  The pins will be press fitted on one half of the mold and sleeves will be press fitted into the other half of the mold.  The wider holes for the sleeves are milled in a separate step, but this step drills holes to prepare for that.  As with the ejector pin holes, the actual gcode does not drill the holes.  Instead, the program should be edited to move to the drill position and then pause, allowing you to use the knee to actually drill the hole.  These holes should be center drilled to start, then step drilled fully through to 15/64” diameter and then reamed with a chucking reamer to 0.2490”.  Z=0 is defined as the faced surface from step 1.  You should slightly chamfer the holes on the left side of the part as you will be pressing a dowel pin into those holes and you want it to not grab when starting.

RPM:  Appropriate for the various drills/reamer

Tool: various drills including 15/64” a chamfering bit and a 0.249” chucking reamer

### Step 8: Mill sleeve holes ###
This program mills the holes for the drill bushings.  The holes are milled 0.001” diameter under to provide a press fit.  Having the through hole drilled ahead of time should make this easier, but make sure chips are cleared as the cut is being made.  Z=0 is defined as the faced surface from step 1.

Tool: 3/8” two flute cutter with at least ½” cutting depth or straight shank

RPM: 3000

### Step 9: Cut around main body rough ###
This step rough cuts around the main body of the mold halves, preparing to separate them.  This is a deep cut with the tool almost always cutting a 100% path, so keep the chips clear.  The operation is defined as “level first” so that the milling switches from one side to the other to give you a chance to clear chips fully.  Z=0 is defined as the faced surface from step 1.

Tool: ½” cutter with at least 1.5” cutting depth (this is more than what is needed for this step, but if you set it up this way you will not need to change the tool for the final step).

Speed: 8ipm

RPM: 3000

### Step 10: Cut around main body finish ###
This step finish cuts around the main body of the mold halves.  This is another deep cut, but it should go much easer as it is just a finishing pass.  It is configured to mill in climb mode to give a better surface finish.

Tool: ½” cutter with at least 1.5” cutting depth (this is more than what is needed for this step, but if you set it up this way you will not need to change the tool for the next step).

Speed: 19ipm

RPM: 3000

### Step 11: Cut around holding flange ###
This final step cuts out the holding flanges on the mold.  Four square holding tabs are left in the bottom of each mold half so the parts will not separate while it is being cut.  This part should end up 1.377” high, but this program will cut through 0.03” further to ensure the part gets separate except for the holding tabs.  Z=0 is defined as the faced surface from step 1.  Ensure the holding tabs in CamBam have a triangle profile to avoid plunge cuts.

Tool: ½” cutter with at least 1.5” cutting depth

Speed: 15ipm

RPM: 3000

### Manual finishing ###
When the machining is done, you can cut the holding tabs with a hack saw and sand the tabs flush.

You can press the drill bushings into the appropriate holes using a machine vice, and ensuring everything is square before applying force.

You should make an alignment block to ensure the dowel pins are pressed straight.  This block is 1/2" thick and has a 1/4" hole that the dowel pins can just slide through.  The pin is put in this block to align it with the hole, and the pin can be pressed in half way using this jig.


## Ejector plate digital design ##
TODO: capture these

## Ejector plate machining ##
The ejector plates are made of 1/4" aluminium stock.

### Step 1: Ejector through holes ###
These need to be center drilled and then through drilled through to 3/16".  The program should be edited to M0 pause after each drill operation and the holes should be cut via the knee.

### Step 2: Attachment through holes in the top plate ###
These need to be center drilled and then through drilled through to 7/32".  The program should be edited to M0 pause after each drill operation and the holes should be cut via the knee.  They will be chamfered step 4.

### Step 3: Attachment through holes in the bottom plate ###
These need to be center drilled and then through drilled through to #21.  They will eventually be tapped by hand to #10-32.  The program should be edited to M0 pause after each drill operation and the holes should be cut via the knee.

### Step 4: 82 degree countersink in top plate attachment holes ###
Zero the tip of the countersink at the top of the plate.  The depth in the program should create an appropriate chamfer.

### Step 5: Mill the ejector through holes ###
Z=0 is the part surface.  This step will mill through the part to create an appropriately "slack" ejector pin through hole.

Tool: 3/16" mill

### Step 6: ###
Z=0 is the part surface.  This step will mill a shoulder in the ejector plate to hold the pin shoulder loosely.

Tool: 3/16" mill

### Step 7: Plate cutout ###
Z=0 is the part surface

Tool: 1/2" mill

### Manual finishing ###
The attachment holes will need to be manually tapped to #10-32 and the socket cap screws from McMaster-Carr referenced below used to hold the plates together.

## Grinding the ejector pins ##
The ejector pins are hardened and will need to be ground to the appropriate length.  With this mold design the ejector pins are on the sprues or off the mold and so the length is not critical, but care should still be taken to get the length correct.  The molder allows <TODO: measure> space when the mold is closed, and pushes the plate flush with the mold when it is open.

## Tooling and hardware ##
The following parts were ordered from McMaster-Carr:
| Part number | Product  | Quantity | Price |
|:------------|:---------|:---------|:------|
| 98378A942 | Precision Perforator Pin, 3/16" Pin Diameter, 2-1/2" Overall Length | 4 | $6.51 Each |
| 9657K349 | Steel Compression Spring, Zinc-Plated Music Wire, 1.50" L, .360" OD, .051" Wire, Packs of 12 | 1 Pack | $9.80 Per Pack |
| 91253A001 | Alloy Steel Flat-Head Socket Cap Screw, 10-32 Thread, 3/8" Length, Black Oxide, Packs of 50 | 1 Pack | $7.81 Per Pack |
| 97395A494 | Corrosion Resistant Dowel Pin, Type 316 Stainless Steel, 1/4" Diameter, 1-1/2" Length, Packs of 5 | 1 | $11.48 Per Pack |
| 8491A115 | Press-Fit Drill Bushing, 0.2510" ID, 13/32" OD, 1/2" Length | 2 | $7.48 Each |

I also got the following tooling, but it is not nearly a complete list:

| Part number | Product  | Quantity | Price |
|:------------|:---------|:---------|:------|
| 2846A125 | Single-Flute High-Speed Steel Countersink, 82 Degree Angle, 1/2" Body Diameter, 1/4" Shank Diameter | 1 | $10.88 Each |
| 8803A38 | Dowel Pin Chucking Reamer, High-Speed-Steel, 1/4" Pin, 0.2480" Reamer Diameter, .2405" Shank | 1 | $19.29 Each |

## Issues and next steps ##
  * The ejector plate needs to be recreated large enough so that the bar that pushes it pushes in the middle, not the very edge.
  * Also all four ejector pins should be used not just two.
  * Holes should be drilled in the mold to hold the springs to help push the ejector plates back.
  * The top of the mold needs a steel bar added so that the injector does not deform the mold

## What would I do differently next time ##
  * I would leave more space between the top of the mold and the ejector pin, since when the injector pressed down on the aluminium mold it deformed it some, ultimately leading to the first mold failure.  The ejector pin hole got crushed and the pin started to bind.
  * I would start each drill operation with a centering drill and use more steps when step drilling.  This would locate the holes much more accurately.
  * I would re-order the ejector pin hole drilling before the sprue cutting so that the ejector pin holes are being drilled on a flat surface.
  * The holes for the drill bushings should be drilled slightly deeper, ~0.005 or so to allow them to press fit in lower than flush.  If they stick out they prevent the mold from closing.
  * I would use drill bushings with a larger ID, 0.253 or 0.254.  When I press fitted them in the dowel pins were too tight and needed to be sanded to fit.  Alternately, machining a slightly larger hole for the bushing would compress them less.
  * A machining step should be added to cut an appropriate groove to hold steel bars for the top of the mold to prevent the injector from deforming the aluminum mold.

# Version 2 notes #
2/27/2015: We recently added some enhancements to the mold and will soon be testing it to see how well it stands up under a production run.  The changes were:

1) Added a steel top plate and re-machined the sprue so that the injector head is pressing against steel.

2) Re-made the ejector plate to be the full height of the mold so that we could put springs above and below the point where the shaft that presses the ejector plate hits the ejector plate.

3) Drilled/milled two 7/16" holes into the back of the ejector-plate-side mold to hold the 1 1/2" springs.

4) Added two stabilizing ejector pins to the ejector plate.  The holes were already reamed through the mold for these pins but we had never actually added them.


With the springs and full-height ejector plate it seems like there will be less binding/racking when ejecting.  Hopefully this will allow the mold to run more reliably.
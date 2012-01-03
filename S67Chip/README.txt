supposedly ideal chip measurements:

39 mm diameter
3.3274 mm thick

chip features:

involute gear 36 teeth, 10 degrees per tooth

milling instructions:

The milling sequence is:

5/8" aluminum stock in the vice, 80x225 big at least
the part x=0,y=0 is at the lower left of the part, so the cutout is at
least 1/4" bigger than that.  So, leave roughly a 1/2" margin in the
-y and +y direction when setting home to be safe.
z=0 is at the part surface

Proper Z=0 setting of each tool is critical and the most likely thing
to mess up.  Z must be re-homed for each file (after each tool
change).  I've made mistakes:

1) Not loading the next file
2) Re-homing the wrong axis
3) Getting the new tool to the part surface but then forgetting to re-home.

The individual files:

sector67-chip-mold-2.s67chip [1-first-pocket].nc:
1/4" end mill with 5 degree draft
rpm around 2500


sector67-chip-mold-2.s67chip [2-gear-detail].nc:
1/32" end mill
rpm around 5000

sector67-chip-mold-2.s67chip [3-texture-drill].nc:
0.025" end mill
rpm around 5000
For this file, check the depth of the "texture" holes and if they are
not deep enough re-home the z slightly deeper.  There is very little
margin for error setting the z=0 on this file.

sector67-chip-mold-2.s67chip [4-sprue].nc:
1/8" ball end mill
around 2500 RPM

sector67-chip-mold-2.s67chip [5-alignment-holes].nc:
3/16" end mill
3000 RPM
spray coolant and vacuum out holes as they are being cut.

sector67-chip-mold-2.s67chip [6-cutout].nc:
1/4" end mill with at least 5/8" shaft

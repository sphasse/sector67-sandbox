# comment the pwm input to insert the abs component
sed -i -e 's/^\(net spindle-vel-cmd.*hm2_5i23.0.pwmgen.00.value$\)/#\1/' sieg_kc4s.hal
sed -i -e 's/^loadrt abs names=abs.spindle.*/loadrt abs names=abs.spindle,abs.pwm/' sieg_kc4s.hal
# for pid loop
sed -i -e 's/^\(net spindle-vel-cmd => abs.pwm.in\)/#\1/' sieg_kc4s.hal
sed -i -e 's/^loadrt scale names=scale.spindle.*/loadrt scale names=scale.spindle,scale.pid.s/' sieg_kc4s.hal


#fix spindle at speed
sed -i -e '/^net spindle-at-speed/d' pyvcp_options.hal
sed -i -e '$ a\
net spindle-at-speed => pyvcp.spindle-at-speed-led' pyvcp_options.hal

sed -i -e '/^OPEN_FILE/d' sieg_kc4s.ini
sed -i -e '/^\[DISPLAY\]$/ a\
OPEN_FILE = /home/scott/linuxcnc/nc_files/examples/lathe_pawn.ngc' sieg_kc4s.ini

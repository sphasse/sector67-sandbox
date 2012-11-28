# comment the pwm input to insert the abs component
sed -i -e 's/^\(net spindle-vel-cmd.*hm2_5i23.0.pwmgen.00.value$\)/#\1/' sieg_kc4s.hal
sed -i -e 's/^loadrt abs names=abs.spindle.*/loadrt abs names=abs.spindle,abs.pwm/' sieg_kc4s.hal
# for pid loop
#sed -i -e 's/^\(net spindle-vel-cmd => abs.pwm.in\)/#\1/' sieg_kc4s.hal
#sed -i -e 's/^loadrt scale names=scale.spindle.*/loadrt scale names=scale.spindle,scale.pid.s/' sieg_kc4s.hal

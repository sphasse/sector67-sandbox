# comment the pwm input to insert the abs component
sed -i -e 's/^\(net spindle-vel-cmd.*hm2_5i23.0.pwmgen.00.value$\)/#\1/' sieg_kc4s.hal
sed -i -e 's/^loadrt abs names=abs.spindle.*/loadrt abs names=abs.spindle,abs.pwm/' sieg_kc4s.hal

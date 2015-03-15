# Frequency-based analog input to LinuxCNC #



# Introduction #
In early 2012 we had a member interested in doing some plunge EDM (electrical discharge machining).  We wanted to repurpose our CNC machines to control the Z axis and so needed a way to feed the analog voltage from the EDM into LinuxCNC.  As we have ample optically isolated digital inputs, we employed an analog to frequency circuit and used LinuxCNC components to convert the frequency to an analog value.

The rest of this page describes that implementation.  It is currently in beta test mode and this page will be updated as we learn better what works and what doesn't.

# Generating a suitable frequency #
There are various ways of generating a suitable frequency from an analog value, including:

  * A Mesa board (THCAD  High isolation A-D accessory) that isolates the analog input and generates frequencies at a programmable rate
  * Dedicated circuits such as an LM331 chip
  * Using a microprocessor like an Arduino

In our case we chose to use an Arduino as we had them in stock.

## Arduino approach ##
Using the Arduino with the following simple program will convert an analog voltage input to a frequency output.

```
/*
Simple analog to frequency converter for use in feeding analog values into
a LinuxCNC system
 */


void setup() {
 // initialize serial communications (for debugging only):
 Serial.begin(9600);
}

void loop() {
 // read the sensor:
 int sensorReading = analogRead(A0);
 // print the sensor reading so you know its range
 //Serial.println(sensorReading);

 // map the pitch to the range of the analog input.
 // change the minimum and maximum input numbers below
 // depending on the range your sensor's giving:
 //  map(value, fromLow, fromHigh, toLow, toHigh)
 int thisPitch = map(sensorReading, 10, 1023, 500, 1000);

 // play the pitch indefinitely
 tone(9, thisPitch);
```

In our case we are scaling the frequency output to between 500 and 1000 Hz.  The digital output (pin 9 in this case) is hooked across an isolated input of our Mesa 7I37TA Isolated I/O daughter card.

# Optical isolation #
As mentioned above, the optical isolation is provided by the Mesa daughterboard.  The timing specs from the manual are:

Opto-isolated inputs turn on on ~5 uSec and off in ~25 uSec.

This limits our input frequency somewhat but is not a show stopper for our application.

# Counting pulses in LinuxCNC #
Although LinuxCNC does not have a dedicated frequency to analog component, one can easily be made by using an encoder component, configuring it for mode and using the velocity output.

# Counting pulses fast enough #
A big challenge with software-based encoders is counting the pulses quickly enough.  The Mesa board will do a great job with on-board encoders, counting as necessary and keeping track of pulse timings very precisely.  However, with the potential rewiring needed to take advantage of on-board 5i23 encoders we decided to go with software-based encoders instead.

In a certain way this is simpler, and in a certain way it is fighting up-stream.  It would have also been possible to create an arduino program to convert the analog value to 8 or 10 bits of resolution and use 8 or 10 digital inputs to read the values.  That would be fast and accurate, but would have consumed lots of digital I/O.

Since in our configuration the Mesa board was previously doing all the heavy lifting counting-wise, we did not have it configured to read gpio frequently enough to count pulses.  The default is to have the Mesa board read gpio on the servo thread, which has a period of 1,000,000 nS by default.  To get around this, it is necessary to bind the read\_gpio function of the mesa component to a faster thread.  This is done by creating a thread like so:

```
loadrt threads name1=encoder-thread period1=50000
```

this needs to be done before loading your motion module, so within the first few lines of your main configuration file.  Then put the following hal configuration where convenient:

```
#http://linuxcnc.org/docs/devel/html/hal/rtcomps.html#sec:Encoder
# hm2_5i23.0.gpio.048.in is the freqeuncy in
# read the gpio frmo the mesa card at the base-thread rate
#loadrt threads name1=edm-thread period1=200000
addf hm2_5i23.0.read_gpio encoder-thread

# load the component
loadrt encoder num_chan=1
setp encoder.0.counter-mode true
#encoder.0.phase-A
net encoder-phase-A encoder.0.phase-A <=  hm2_5i23.0.gpio.048.in

# set the velocity of the encoder for a proper scale
setp encoder.0.position-scale 1.0
# set the velocity out to feed the analog input
net analog-0-in <= encoder.0.velocity
net analog-0-in => motion.analog-in-00  
# add the component to the appropriate threads
addf encoder.update-counters encoder-thread
addf encoder.capture-position servo-thread
```

to load the software encoder and bind it as appropriate.  You'll need to pick the appropriate gpio for your setup of course.

This could all be done with a parallel port as well, and in that case the encoder.update-counters would be bound to the base-thread and it would not be necessary to bind the hm2\_5i23.0.read\_gpio to any thread.  The encoder-thread would simply go away completely in favor of the base-thread.

# Making use of the analog value #
We are configuring the motion.analog-in-00 pin to hold the analog value, so we can use the M66 gcode commands to read this value.

The program below shows how we are using the analog value to make a plunge/stay/retreat decision for our EDM system.  The values below are not realistic, but simply for testing purposes using a potentiometer as the analog input.

```
(AXIS,stop)
(stop the preview which will not complete with a while loop)

(program to plunge and retreat based on an analog value)
(developed for use with EDM at sector67)
#1=0 (Z safe height)
#2=-1 (ultimate Z depth)
#3=0.0001 (Z step)
(all thresholds between 500 and 1000 )
#5=750 (upper hold threshold, higher than this plunges )
#6=650 (lower hold threshold, lower than this retreats)

#4=#1 (current depth, updated as needed)

F10

G1 Z#1

O101 while [#4 gt #2]
    M66 E0 L0
    (the analog value is stored in #5399)
    O102 if [#5399 gt #5]
        O103 if [#5399 GT #6]
            (voltage is high, plunge forward if not at target depth)
            O104 if [#4 gt #2]
                #4 = [#4 - #3]
                G1 Z#4
            O104 endif
        O103 else
            (voltage is fine, stay put)
        O103 endif
    O102 else
        (voltage is low, move up if below safe height)
        O105 if [#4 lt #1]
            #4 = [#4 + #3]
            G1 Z#4
        O105 endif
    O102 endif
O101 endwhile

#4 = #1
G1 Z#4 (back off when finished to the safe height)

M30

```

In basic testing this program seems to work as expected.

# Further refinements #
There is still more jitter/interpolation than expected and the manageable frequencies are lower than expected as well (topping out around 1500Hz with a 50000 uS encoder thread).  Some analysis is probably needed to determine why this is.  1500Hz has a period of 666 uS.  Even assuming 25uS delay on both transitions of the optical isolation, and sampling each 50% duty cycle twice, we should still be able to count much higher frequencies.  More math and perhaps some scope analysis here would be helpful.

What we have now should be workable for our three-band EDM decision making.
# Introduction #
This page describes a technique for PID tuning Glentek/Anilam SAM7215 servo amps when used with LinuxCNC.



# Details #

An excellent book on the subject of PID tuning is _Control System Design Guide_ by George Ellis [[1](PIDTuningGlentekAmps#1.md)].  It is basically an academic text book with hands-on software-based exercises.  Chapters 6 and 17 in particular provide a solid background in PID tuning for position control.

Our basic approach is from [[1](PIDTuningGlentekAmps#1.md)] chapter 17:

> The primary strength of P/PI control is simple tuning.  The PI velocity loop is tuned for maximum performance and then the position gain is increased to just below the value where overshoot appears.

We will apply this basic technique in our tuning.  Further:

> The primary shortcoming is that the method allows stead-state position error (following error) in the presence of a constant-velocity command

These are fairly common in the CNC world.  Continuing:

> Fortunately, this can be corrected with velocity feed-forward, as will be discussed later.  Another problem is that when the connection from position loop output to velocity loop input is analog, offset in the signal will generate proportionate position error when the system is at rest.

I have observed both of these problems in our P/PI system without feed forward tuning.




---

### References ###
##### 1 #####
[Control System Design Guide, George Ellis](http://www.amazon.com/Control-System-Design-Guide-Third/dp/0122374614)

##### 2 #####
[Feed forward control article](http://en.wikipedia.org/wiki/Feedforward_control)
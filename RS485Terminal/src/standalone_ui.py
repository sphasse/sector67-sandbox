
import threading
import time

from spindleblokutils import DataUtils
from spindleblokutils import MockCommandChannel
from spindleblokutils import RS485Command
from spindleblokutils import SpindleBlok
from spindleblokutils import Spindle


"""
A class to encapsulate the process of talking to a spindle.  It sets up a command channel for talking
with the VFD, which can currently be a serial channel or mock channel depending on the requirements

The class starts a thread to periodically read requested input and update requested output.  The hope
is that this class makes it fairly straightforward to bolt on a command line ui, simple GUI or HAL interface
to control the underlying spindle.  Basically designed to be easy to hook up to the hal motion component
for the spindle:

TODO: get
    
"""
class SpindleInterface:

    requestedRPM = 0
    requestedState = Spindle.STOPPED_STATE
    requestedDirection = Spindle.Direction

    alive = False
    
    currentRPM = 0
    currentState = Spindle.STOPPED_STATE
    currentVDC = 0
    currentDirection = Spindle.DIRECTION_CW
        
    def setup(self):
        #setup the command channel, either real or mock
        #self.command_channel = SerialCommandChannel.get_instance()
        self.command_channel = MockCommandChannel.get_instance()
        self.command_channel.start()
        self.vfd = SpindleBlok(self.command_channel)
        self.vfd.set_serial_control()
        self.vfd.set_comm_timer_max(96)
        self.vfd.set_rpm(0)
        self.vfd.request_stop()

    """
    The main loop of the UI.  TODO: try to make this less SpindleBlok specific (make the spindleblok interface more of a generic VFD)
    """
    def _updater(self):
        self.updating = True
        while self.alive:
            time.sleep(0.1)
            if (self.command_channel.alive):
                self.vfd.set_rpm(self.requestedRPM)
                #set RPM each time regardless
                if (self.requestedState != self.currentState):
                    if (self.requestedState == Spindle.STOPPED_STATE):
                        self.vfd.request_stop()
                    elif (self.requestedState == Spindle.STARTED_STATE):
                        self.vfd.request_start()
                    else:
                        raise Exception("The state needs to be either stopped or started")
                    self.currentState = self.requestedState
                if (self.requestedDirection != self.currentDirection):
                    if (self.requestedDirection == Spindle.DIRECTION_CW):
                        #self.vfd.request_stop()
                    elif (self.requestedDirection == Spindle.DIRECTION_CCW):
                        #self.vfd.request_start()
                    else:
                        raise Exception("The state needs to be either stopped or started")
                    self.currentState = self.requestedState

                self.currentRPM = self.vfd.get_rpm()
                self.currentVDC = self.vfd.get_vdc_dsp()

            else:
                # perhaps try to re-establish serial connectivity via setup
                # for now, raise an exception
                raise Exception("The command channel is no longer alive, cannot send commands.")
        self.updating = False

    def start(self):
        self.alive = True
        # start serial->console thread
        self._updater_thread = threading.Thread(target=self._updater)
        self._updater_thread.setDaemon(1)
        self._updater_thread.start()
         
    def shutdown(self):
        self.alive = False
        #wait for the main loop to complete all of the main loop commands
        while (self.updating):
            time.sleep(0.1)
        self.vfd.set_rpm(0)
        self.vfd.request_stop()
        self.vfd.set_comm_timer_max(0)
        self.vfd.set_local_control()
        #shutdown the command channel
        self.command_channel.stop()
        
"""
The main script
"""
interface = SpindleInterface()

interface.setup()

interface.start()
try:
    while (interface.alive):
        command = raw_input("VFD command >")
        if (command == "exit"):
            interface.shutdown()
        elif (command == "start"):
            interface.requestedState = Spindle.STARTED_STATE
        elif (command == "stop"):
            interface.requestedState = Spindle.STOPPED_STATE
        elif (command == "forward"):
            interface.requestedDirection = Spindle.DIRECTION_CW
        elif (command == "reverse"):
            interface.requestedDirection = Spindle.DIRECTION_CCW
        elif (command.startswith("rpm")):
            try:
                rpm = int(command.split(" ")[1])
                interface.requestedRPM = rpm
            except ValueError:
                print "RPM must be a number"
        else:
            print("STATE=" + str(interface.currentState) + ",DIR=" + str(interface.currentDirection) + ",RPM=" + str(interface.currentRPM) + ", VDC=" + str(interface.currentVDC))
except KeyboardInterrupt:
    print "exiting via KeyboardInterrupt"

print("goodbye")
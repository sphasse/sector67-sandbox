
import binascii
import threading, time, sys, serial

"""

From the SpindleBlok manual:

To set up serial control for the SpindleBlok VFD:

You should enable the control method you have chosen by setting or clearing bits 8 and 9 of C01 (drive_mode).

Feedback from the drive is monitored on a periodic basis. This consists of reading 
parameters of interest from the Feedback Page (D00 - D1A). Commonly read parameters 
are D00 (drive_state), D03 (i_mag), D06 (vout), D09 (omega_m_dsp), or D0B (torque). 
Start and stop commands are issued, as needed, by writing to parameter C00 (drive_command).

The speed setpoint is written to, as needed, at parameter C02 (omega_cmd_save) or
parameter C03 (omega_cmd_save_nv). The difference between these two parameters
is that C03 (omega_cmd_save_nv) is saved in both RAM and non-volatile ee-prom. The
value written will be stored during power down and retrieved on power up. Parameter
C02 (omega_cmd_save) is only saved in RAM and will be lost on power down. You
should write to C02 (omega_cmd_save) if you write the speed command often as the
non-volatile ee-prom has only a 100,000 write cycle life. If your control system updates
the speed command each time it runs or on a periodic basis, use parameter C02
(omega_cmd_save). If you want to initialize the speed command once and not write to it
again, use parameter C03 (omega_cmd_save_nv).

The Spindleblok will need to have run_enable (digital input 1) on the local I/O asserted to
be able to run. This is often used as a mechanical emergency stop. You can also simply
jumper pin 9 (digital input 1) to pin 8 (digital ground) to enable the drive. An additional

"""



"""
This class encapsulates the functionality needed to deal with the various data types sent
and expected by the SpindleBlok.  Python 2.x does not have very good built-in support for
binary arrays, two's compliement numbers, or preserving the length of hex string data when
there are leading zeros.  So this class encapsulates that needed functionality.
"""
class DataUtils:
    """
    Expects a string of hex data as returned from, e.g. "00ff".
    Pretty prints the binary data in columns with descriptions.
    Preserves leading zeros when printing.
    """
    @staticmethod
    def dump_bits(data, descriptions):
        bits = DataUtils.hex_string_to_bit_string(data)

        if (len(bits) != len(descriptions)):
            raise Exception("I cannot display the provided data, the descriptions do not match the data sent (size difference: data " + str(len(bits)) + ", descriptions " + str(len(descriptions)) + ")")

        print "Data: 0x" + data

        for idx, val in enumerate(bits):
            bitdata = ""
            for j in range(len(bits)):
                if (j > 0 and j % 4 == 0):
                    bitdata = bitdata + " "
                if (j == idx):
                    bitdata = bitdata + val
                else:
                    bitdata = bitdata + "."        
            print '%(bitdata)s = %(description).50s' % {'bitdata': bitdata, 'description': descriptions[idx]}

    """
    Converts text hex data ("abcd") representing a signed (two's compliment) integer to an int.  The text data 
    should be zero padded if necessary to accurately represent the intended length of the signed int.
    """
    @staticmethod
    def hex_string_to__signed_int(data):
        bits = DataUtils.hex_string_to_bit_string(data)
        x = int(data, 16)
        if bits[0] == '1': # "sign bit", big-endian
            x -= 2**len(bits)
        return x

    """
    Converts an int to text hex data ("abcd") representing a signed (two's compliment) number.  Doing 
    this correctly requires the target data size in bits to be known, so that must be passed as well.
    The passed length must be a multiple of 8
    """
    @staticmethod
    def signed_int_to_hex_string(data, length):
        format = "%0." + str(length/4) + "x"
        if (data >= 0):
            return format % data
        else:
            data = data
            result = format % abs(data)
            mask = format % (2**length - 1)
            # flip all the bits
            result = DataUtils.apply_xor_bit_mask(result, mask)
            # add one to the result
            i = int(result, 16)
            i = i + 1
            return format % i

    """
    expects a string like "ab01" and returns bytes representing that data.  Does not preserve leading zeros.
    """
    @staticmethod
    def hex_string_to_bytes(data):
        return binascii.unhexlify(data)


    """
    converts a hex string to bit representation, preserving leading zeros.
    """
    @staticmethod
    def hex_string_to_bit_string(data):
        data = data.lower()
        s=''
        t={'0':'0000','1':'0001','2':'0010','3':'0011',
           '4':'0100','5':'0101','6':'0110','7':'0111',
           '8':'1100','9':'1101','a':'1110','b':'1111',
           'c':'1100','d':'1101','e':'1110','f':'1111'}
        for c in data:
            s+=t[c]
        return s

    """
    expects bytes and returns a string with the hex representation of the data string like "ab".
    Preserves leading zeros, requires an even number of hex digits.
    """
    @staticmethod
    def bytes_to_hex_string(data):
        size = len(data) * 2 # twice as many hex digits, preserve leading zeros
        format = "%0." + str(size) + "s"
        hexString = binascii.hexlify(data)
        return format % hexString


    """
    takes in a string of hex representing a bit mask and a string of hex data and apply the mask to the data.
    Returns a string of hex data.  Preserves leading zeros.
    """
    @staticmethod
    def apply_or_bit_mask(mask, data):
        if (len(mask) != len(data)):
            raise Exception("I cannot apply a mask to data of a different size (size difference: mask " + str(len(mask)) + ", data " + str(len(data)) + ")")
        size = len(data)    
        maskData = int(mask,16)
        byteData = int(data, 16)
        format = "%0." + str(size) + "x"
        result = maskData | byteData
        # ensure the returned result is two characters long
        formatted = format % result
        return formatted

    """
    takes in a string of hex representing a bit mask and a string of hex data and apply the mask to the data.
    Returns a string of hex data.  Preserves leading zeros.
    """
    @staticmethod
    def apply_and_bit_mask(mask, data):
        if (len(mask) != len(data)):
            raise Exception("I cannot apply a mask to data of a different size (size difference: mask " + str(len(mask)) + ", data " + str(len(data)) + ")")
        size = len(data)    
        maskData = int(mask,16)
        byteData = int(data, 16)
        format = "%0." + str(size) + "x"
        result = maskData & byteData
        # ensure the returned result is two characters long
        formatted = format % result
        return formatted

    """
    takes in a string of hex representing a bit mask and a string of hex data and apply the mask to the data.
    Returns a string of hex data.  Preserves leading zeros.
    """
    @staticmethod
    def apply_xor_bit_mask(mask, data):
        if (len(mask) != len(data)):
            raise Exception("I cannot apply a mask to data of a different size (size difference: mask " + str(len(mask)) + ", data " + str(len(data)) + ")")
        size = len(data)    
        maskData = int(mask,16)
        byteData = int(data, 16)
        format = "%0." + str(size) + "x"
        result = maskData ^ byteData
        # ensure the returned result is two characters long
        formatted = format % result
        return formatted

class RS485Command:
    def __init__(self, command_string):
        command = command_string.rstrip('\n')
        self.action_char = command[0]
        self.address = command[1]
        self.cmd = command[2:5]
        self.data = command[5:-1]
        self.checksum = command[-1]
        self.full_string = self.action_char + self.address + self.cmd + self.data + self.checksum
        
    def is_valid(self):
        check = RS485Utils.compute_checksum(self.action_char + self.address + self.cmd + self.data)
        if (check == self.checksum):
            return True
        else:
            return False
    
    """
    Create an outgoing command, computing the checksum
    """
    @staticmethod
    def create_outgoing_command(action, address, command, data):
        result = action + address + command + data
        checksum = RS485Utils.compute_checksum(command)
        result = result + checksum
        return RS485Command(result)

    """
    Parse an incoming command
    """
    @staticmethod
    def parse_incoming_command(command):
        return RS485Command(command)

"""
This class holds helper functions for RS485 communication
"""
class RS485Utils:
    """
    Computes the RS485 checksum per the SpindleBlok user manual.
    """
    @staticmethod
    def compute_checksum(command):
        sum = 0
        for c in command:
            sum = sum + ord(c)
        sum = sum & 0x7F
        sum = sum | 0x40
        return chr(sum)
    
    @staticmethod
    def generate_command(action, address, command, data):
        result = action + address + command + data
        checksum = RS485Utils.compute_checksum(command)
        result = result + checksum
        return result

"""
This class represents a physical SpindleBlok VFD.  It stores the state of the drive and has methods for
executing commands and reading state.  
"""
class SpindleBlok:
    STOPPED = 0
    STARTED = 1
    def __init__(self, command_channel, address=1):
        self.command_channel = command_channel
        self.address = str(address)
        # get constants
        self.kv = self.get_kv()
        self.max_speed = self.get_max_speed()
        self.ki_imag = self.get_ki_imag()

    kv = 0
    max_speed = 0
    ki_imag = 0
    currentState = STOPPED

    """
    C01:
    This parameter is bit defined. Set and clear the appropriate bits to set the drive
    in the desired mode. This parameter should be changed by performing a readmodify-
    write so that only the intended bits are changed.
    """
    C01_DESCRIPTONS = [
     "Bit 0 set: Ramp to stop  Bit 0 clr: Coast to stop.",
     "Bit 1 set: Calculate motor parameters from nameplate data on start.  Bit 1 clr: Do not calc motor parms.",
     "Bit 2 set: Normal communications mode. The check-sum is verified on each message. Bit 2 clr: Ignore check-sum on all serial communications.",
     "Bit 3 set: Perform standard commission only on a commission request.  Bit 3 clr: Perform standard and extended commission on a commission request.",
     "Bit 4 set: Request sensorless flux vector mode.  Bit 4 clr: Request open loop mode.",
     "Bit 5 set: Forward direction is enabled.  Bit 5 clr: Forward direction is disabled.",
     "Bit 6 set: Reverse direction is enabled.  Bit 6 clr: Reverse direction is disabled.",
     "Bit 7 set: Acceleration and deceleration ramps are modified to maintain constant torque current for an inertial load during field weakening.  Bit 7 clr: Linear acceleration and deceleration ramps.",
     "Bit 8 set: Serial setpoint control.  Bit 8 clr: Local setpoint control.",
     "Bit 9 set: Serial start control.  Bit 9 clr: Local start control.",
     "Bit 10 set: Use default set of speed regulator gains...  Bit 10 clr: Use high inertia set of speed regulator gains...",
     "Bit 11 Reserved, write as 1",
     "Bit 12 set: Pull up digital inputs internally to 5 volts.  Bit 12 clr: Pull down digital inputs 1-6 internally to ground.",
     "Bit 13 set: Analog input bi-polar mode.  Bit 13 clr: Analog input uni-polar mode.",
     "Bit 14 set: Run / Fwd-Rev mode.  Bit 14 clr: Run-Fwd / Run-Rev mode.",
     "Bit 15 Reserved, write as 1"]


    """
    C00:
    This parameter is bit defined. Sending a command to the drive is accomplished
    by setting this parameter with the appropriate bit cleared.
    The command is acknowledged when the corresponding bit is set. Note that to
    cause a processor reset, the processor reset bit must be cleared AND all other
    bits must be set.
    """ 
    C00_DESCRIPTONS = [
     "Bit 0: Stop request",
     "Bit 1: Start request",
     "Bit 2: Commission request",
     "Bit 3: reserved (always write as 1)",
     "Bit 4: Clear External fault",
     "Bit 5: External fault",
     "Bit 6: Clear the fault queue.",
     "Bit 7: Reset serial communications.",
     "Bit 8: Set Factory Default Autotune Parameters",
     "Bit 9: reserved (always write as 1)",
     "Bit 10: reserved (always write as 1)",
     "Bit 11: IO Reset",
     "Bit 12: Calc Motor",
     "Bit 13: reserved (always write as 1)",
     "Bit 14: reserved (always write as 1)",
     "Bit 15: Processor Reset"]

    D00_DESCRIPTONS = [
     "Bit 0 set: Reverse direction.  Bit 0 clr: Forward direction",
     "Bit 1: Reserved",
     "Bit 2 set: Inverter is running.  Bit 2 clr: Inverter is off",
     "Bit 3 set: Open loop control mode.  Bit 3 clr: Sensorless flux vector control mode.",
     "Bit 4 set: Drive commissioning.  Bit 4 clr: Drive not commissioning.",
     "Bit 5 set: Speed and flux tracking regulators are on.  Bit 5 clr: Speed and flux tracking regulators are off.",
     "Bit 6: Reserved",
     "Bit 7: Reserved"]

    """
    drive API version 0.1 below
    """
    def get_signed_int(self, command, timeout=1):
        request = RS485Command.create_outgoing_command("$", self.address, command, "")
        self.command_channel.send_command(request)
        reply = self.command_channel.receive_reply(timeout)
        return DataUtils.hex_string_to_signed_int(reply.data)
    
    def get_hex_string(self, command, timeout=1):
        request = RS485Command.create_outgoing_command("$", self.address, command, "")
        self.command_channel.send_command(request)
        reply = self.command_channel.receive_reply(timeout)
        return reply.data
        
    """
    Read all bits from C01.  Returns two bytes of hex string data.
    """
    def read_drive_mode(self, data):
        return self.get_hex_string("C01")

    """
    Write all bits from C01.  C01 should in general be changed in a read->modify->write mode to 
    avoid setting or clearing wrongly.  Expects two bytes of hex string data (e.g. "ffff")
    """
    def write_drive_mode(self, data):
        raise NotImplementedError

    """
    Sets the correct bits on the drive mode (C01) to enable serial control
    """
    def set_serial_control(self):
        raise NotImplementedError

    """
    Sets the correct bits on the drive mode (C01) to enable local control
    """
    def set_local_control(self):
        raise NotImplementedError

    """
    Non-NVRam RPM set, can be called frequently, set via C02
    """
    def set_rpm(self):
        raise NotImplementedError

    def request_start(self):
        raise NotImplementedError

    """
    Set a bit in the 
    """
    def request_stop(self):
        raise NotImplementedError

    """
    Read from D00
    """
    def get_drive_state(self):
        return self.get_hex_string("D00")

    """
    Read from D03
    """
    def get_i_mag(self):
        return self.get_signed_int("D03")

    """
    Output voltage, read from D06
    """
    def get_vout(self):
        return self.get_signed_int("D06")

    """
    DC link voltage, * kv, read from D07
    This method scales the voltage to the actual value
    """
    def get_vdc_dsp(self):
        result = self.get_signed_int("D07") / self.kv
        return result

    """
    The 10 * Hz of the drive, read via D08
    """
    def get_omega_dsp(self):
        result = self.get_signed_int("D08") / 10
        return result

    """
    The RPM of the drive, read via D09
    """
    def get_omega_m_dsp(self):
        return self.get_signed_int("D09")

    """
    Read via D0A
    """    
    def get_heatsink_temp(self):
        return self.get_signed_int("D0A")

    """
    Read via D0C
    """    
    def get_power_in(self):
        return self.get_signed_int("D0C")

    """
    Read via D0D
    """ 
    def get_elapsed_lo(self):
        return self.get_signed_int("D0D")

    """
    Read via D0E
    """
    def get_elapsed_hrs(self):
        return self.get_signed_int("D0E")
 
    """
    A scaling factor, read via A08
    """
    def get_ki_imag(self):
        return self.get_signed_int("A08")

    """
    A scaling factor, read via A09 
    """
    def get_kv(self):
        return self.get_signed_int("A09")

    """
    The max speed in RPM, read via F00  
    """
    def get_max_speed(self):
        return self.get_signed_int("F00")
    
    """
    0.052 second increments to wait before a serial communication timeout causes problems, set via J02
    1 second is roughly 19 increments
    5 seconds is roughly 96 increments
    """
    def set_comm_timer_max(self):
        raise NotImplementedError


"""
An abstract command channel
"""
class CommandChannel:
    incoming_commands = []
    outgoing_commands = []
    """
    called by a client to send a command
    """
    def send_command(self, command):
        self.outgoing_commands.append(command)
    
    """
    called by a client wishing to receive a command in reply to the one they sent
    """
    def receive_reply(self, timeout=1):
        delay = 0.1
        i = 0.0
        while (i < timeout):
            i = i + delay
            if (len(self.incoming_commands) > 0):
                reply = self.incoming_commands.pop(0)
                return reply
            time.sleep(delay)
        raise Exception("This should be some sort of delay exceeded exception");
    

"""
A class represeting a serial channel to communicate with the SpindleBlok
"""
class SerialCommandChannel(CommandChannel):
    def __init__(self, port, baudrate, parity, rtscts, xonxoff):
        try:
            self.serial = serial.serial_for_url(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        except AttributeError:
            # happens when the installed pyserial is older than 2.5. use the
            # Serial class directly then.
            self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        self.dtr_state = True
        self.rts_state = True
        self.break_state = False

    def start(self):
        self.alive = True
        # start receiving thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()
        # start sending thread
        self.transmitter_thread = threading.Thread(target=self.writer)
        self.transmitter_thread.setDaemon(1)
        self.transmitter_thread.start()

    def stop(self):
        self.alive = False
        self.join()

    def join(self):
        self.transmitter_thread.join()
        self.receiver_thread.join()
        
 
    
    def reader(self):
        """loop and copy serial->console, decoding full commands"""
        try:
            r_cmd = ""
            while self.alive:
                data = self.serial.read(1)

                for character in data:
                    if character == '\r':
                        self.incoming_commands.append(r_cmd)
                        r_cmd = ""
                    else:
                        r_cmd = r_cmd + data
        except serial.SerialException:
            self.alive = False
            raise


    def writer(self):
        """loop and copy commands to the serial port
        """
        try:
            while self.alive:
                if (len(self.incoming_commands) > 0):
                    command = self.incoming_commands.pop(0)
                    command = command + '\r'
                    for c in command:
                        self.serial.write(c)  # send character
                time.sleep(0.1)
        except:
            self.alive = False
            raise


"""
A mock command channel for testing the vfd offline.  This mock fakes returned data.
"""
class MockCommandChannel(CommandChannel):  
    def __init__(self):
        pass
        
    def start(self):
        self.alive = True
        # start command handling thread
        self.transmitter_thread = threading.Thread(target=self.writer)
        self.transmitter_thread.setDaemon(1)
        self.transmitter_thread.start()
        
    def stop(self):
        self.alive = False
        self.join()

    def join(self):
        self.transmitter_thread.join()

    def writer(self):
        """
        handle mock commands, sending an appropriate reply to requests
        """
        try:
            while self.alive:
                if (len(self.outgoing_commands) > 0):
                    command = self.outgoing_commands.pop(0)
                    time.sleep(0.1)
                    # create a mock reply to the outgoing request
                    if (command.cmd == "C00"):
                        reply = RS485Command.create_outgoing_command("$", "1", "C00", "ffff")
                        self.incoming_commands.append(reply)
                    elif (command.cmd == "C01"):
                        reply = RS485Command.create_outgoing_command("$", "1", "C01", "ffff")
                        self.incoming_commands.append(reply)
                    else:
                        raise Exception("I did not recognize the command to return a mock response: " + command.full_string)
        except:
            self.alive = False
            raise

"""
A class to encapsulate a simple command line user interface
"""
class UserInterface:

    requestedRPM = 0
    """
    returns an object that can be started to initiate serial communications
    """
    def get_serial_channel(self):
        port = 0
        baudrate = 9600
        parity = 'N'
        rtscts = False
        xonxoff = False
        try:
            channel = SerialCommandChannel(
                port,
                baudrate,
                parity,
                rtscts=rtscts,
                xonxoff=xonxoff
            )
        except serial.SerialException, e:
            sys.stderr.write("could not open port %r: %s\n" % (port, e))
            sys.exit(1)
            
        return channel

    def setup(self):
        #setup serial reader and writer threads
        self.serial_channel = self.get_serial_channel()
        self.serial_channel.start()
        self.vfd = SpindleBlok(self.serial_channel)
        #set_serial_control()
        #set_rpm(0)
        #request_stop()
        #set_comm_timer_max(96)    

    """
    The main loop of the UI.  TODO: try to make this less SpindleBlok specific (make the spindleblok interface more generic
    """
    def loop(self):
        if (self.serial_channel.alive):
            self.driveState = self.vfd.get_drive_state()
            
            """
            set_rpm(requestedRPM)
            requestedMode = getRequestedMode()
            if (requestedState != currentState):
                if (requestedState == SpindleBlok.STOPPED):
                    request_stop()
                else if (requestedState == SpindleBlok.STARTED):
                    request_start()
                else:
                    raise Exception("The state needs to be either stopped or started")
                currentState = requestedState
            """
            self.currentRPM = self.vfd.get_omega_m_dsp()
            self.currentVDC = self.vfd.get_vdc_dsp()
            
        else:
            #try to establish serial connectivity via setup
            # for now, raise an exception
            raise Exception("lost serial connectivity")
         
    def shutdown(self):
        self.vfd.set_rpm(0)
        self.vfd.request_stop()
        self.vfd.set_comm_timer_max(0)
        self.vfd.set_local_control()
        #shutdown serial reader and writer threads
        self.serial_channel.stop()




"""
"""
DataUtils.dump_bits("ffab", SpindleBlok.C00_DESCRIPTONS)

DataUtils.dump_bits(DataUtils.apply_or_bit_mask("00c0", "F0F0"), SpindleBlok.C01_DESCRIPTONS)

"""
HAL motion spindle pins:
motion.spindle-at-speed
    (bit, in) Motion will pause until this pin is TRUE, under the following conditions: before the first feed move after each spindle start or speed change; before the start of every chain of spindle-synchronized moves; and if in CSS mode, at every rapid to feed transition. This input can be used to ensure that the spindle is up to speed before starting a cut, or that a lathe spindle in CSS mode has slowed down after a large to small facing pass before starting the next pass at the large diameter. Many VFDs have an "at speed" output. Otherwise, it is easy to generate this signal with the HAL near component, by comparing requested and actual spindle speeds.
motion.spindle-brake
    (bit, out) TRUE when the spindle brake should be applied.
motion.spindle-forward
    (bit, out) TRUE when the spindle should rotate forward.
motion.spindle-index-enable
    (bit, I/O) For correct operation of spindle synchronized moves, this pin must be hooked to the index-enable pin of the spindle encoder. 
motion.spindle-on
    (bit, out) TRUE when spindle should rotate.
motion.spindle-reverse
    (bit, out) TRUE when the spindle should rotate backward
motion.spindle-revs
    (float, in) For correct operation of spindle synchronized moves, this signal must be hooked to the position pin of the spindle encoder. The spindle encoder position should be scaled such that spindle-revs increases by 1.0 for each rotation of the spindle in the clockwise (M3) direction.
motion.spindle-speed-in
    (float, in) Feedback of actual spindle speed in rotations per second. This is used by feed-per-revolution motion (G95). If your spindle encoder driver does not have a velocity output, you can generate a suitable one by sending the spindle position through a ddt component.
motion.spindle-speed-out
    (float, out) Commanded spindle speed in rotations per minute. Positive for spindle forward (M3), negative for spindle reverse (M4).
motion.spindle-speed-out-rps
    (float, out) Commanded spindle speed in rotations per second. Positive for spindle forward (M3), negative for spindle reverse (M4).
"""

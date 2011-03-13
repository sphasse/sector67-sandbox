#!/usr/bin/env python
"""
A python script to send a file via a serial port
Copyright (C) 2010 Scott Hasse <scott.hasse@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.


designed for DNC drip feeding ("direct numeric control")
of CNC mill machines that talk via simple serial port data
transfer

Developed by Scott Hasse for use at http://sector67.org

Serial transfer adapted from http://pyserial.sourceforge.net/examples.html#miniterm
ProgressBar adapated from code at http://www.5dollarwhitebox.org/drupal/node/65 and
http://code.activestate.com/recipes/168639/

Pyserial apparently does not fully implmement xon/xoff flow control, so it is current
implemented in this software.  Currently, serial flow control will necessarily be 
enabled even if you do not specify it as a command-line option.

If you do not know what serial port to use, you can use the tools listed under the
"Finding serial ports" section here:
http://pyserial.sourceforge.net/examples.html
to list your serial ports.
"""


import sys, os, threading     
import time
try:
    import serial
except ImportError:
    sys.stderr.write("ERROR: This script cannot import serial.  You may need to install pyserial into your Python installation.\n")
    sys.stderr.write("More information on pyserial can be found at http://pyserial.sourceforge.net/\n")
    sys.exit(1)

"""
Unfortunately, it is necessary to use a platform dependent way to read single characters from i
the console.  This class implements that platform-specific method.
"""
global console

if os.name == 'nt':
    import msvcrt
    class Console:
        def __init__(self):
            pass

        def setup(self):
            pass    # Do nothing for 'nt'

        def cleanup(self):
            pass    # Do nothing for 'nt'

        def getkey(self):
            while 1:
                z = msvcrt.getch()
                if z == '\0' or z == '\xe0':    # functions keys
                    msvcrt.getch()
                else:
                    if z == '\r':
                        return '\n'
                    return z
                    
        def keypressed(self):
            return msvcrt.kbhit()

    console = Console()

elif os.name == 'posix':
    import termios, select, sys, tty
    class Console:
        """
        This Console implementation sets the terminal for non-buffered IO, and
        makes sure the terminal gets reset to the original settings on exit.
        """
        def __init__(self):
            self.fd = sys.stdin.fileno()

        def setup(self):
            self.old_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

        def getkey(self):
            c = sys.stdin.read(1)
            return c

        def cleanup(self):
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)

        def keypressed(self):
            return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])
            
    console = Console()

    def cleanup_console():
        console.cleanup()

    console.setup()
    sys.exitfunc = cleanup_console      #terminal modes have to be restored on exit.

else:
    raise "Sorry no implementation for your platform (%s) available." % sys.platform



"""
A class to encapsulate the command line progress bar functionality.
"""
class ProgressBar:
    def __init__(self, min_value = 0, max_value = 100, width=50):
        self.char = '='
        self.bar = ''
        self.min = min_value
        self.max = max_value
        self.span = max_value - min_value
        self.width = width
        self.amount = 0       # When amount == max, we are 100% done 
        self.update_amount(0) 
 
    def update_amount(self, new_amount = None):
        """
        Update self.amount with 'new_amount', and then rebuild the bar 
        string.
        """
        if not new_amount: new_amount = self.amount
        if new_amount < self.min: new_amount = self.min
        if new_amount > self.max: new_amount = self.max
        self.amount = new_amount
        self.build_bar()
 
    def build_bar(self):
        """
        Figure new percent complete, and rebuild the bar string based on 
        self.amount.
        """
        diff = float(self.amount - self.min)
        percent_done = int(round((diff / float(self.span)) * 100.0))
 
        # figure the proper number of 'character' make up the bar 
        all_full = self.width - 2
        num_hashes = int(round((percent_done * all_full) / 100))
 
        # build a progress bar with self.char and spaces (to create a 
        # fixed bar (the percent string doesn't move)
        self.bar = self.char * num_hashes + ' ' * (all_full-num_hashes)
 
        percent_str = "(" + str(percent_done) + "%)"
        count_str = str(self.amount) + " of " + str(self.max)
        self.bar = '[ ' + self.bar + ' ] ' + count_str + " " + percent_str
 
    def __str__(self):
        return str(self.bar)
 

class SerialTerm:

    CONVERT_CRLF = 2
    CONVERT_CR   = 1
    CONVERT_LF   = 0
    NEWLINE_CONVERISON_MAP = ('\n', '\r', '\r\n')
    LF_MODES = ('LF', 'CR', 'CR/LF')

    def __init__(self, port, baudrate, parity, rtscts, xonxoff, convert_outgoing=CONVERT_CRLF, bytesize=7, interface=None):

        try:
            self._serial = serial.serial_for_url(port, baudrate, bytesize=bytesize, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        except AttributeError:
            # happens when the installed pyserial is older than 2.5. use the
            # Serial class directly then.
            self._serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1, bytesize=bytesize)
        self._convert_outgoing = convert_outgoing
        self._newline = self.NEWLINE_CONVERISON_MAP[self._convert_outgoing]
        self._paused = False
        self._interface = interface

    def start(self):
        self._alive = True
        # start serial->console thread
        self._receiver_thread = threading.Thread(target=self._reader)
        self._receiver_thread.setDaemon(1)
        self._receiver_thread.start()

    def stop(self):
        self._alive = False

    def join(self, transmit_only=False):
        self._receiver_thread.join()

    def dump_port_settings(self):
        sys.stderr.write("Serial settings: %s %s,%s,%s,%s\n" % (
            self._serial.portstr,
            self._serial.baudrate,
            self._serial.bytesize,
            self._serial.parity,
            self._serial.stopbits,
        ))
        sys.stderr.write('--- software flow control %s\n' % (self._serial.xonxoff and 'active' or 'inactive'))
        sys.stderr.write('--- hardware flow control %s\n' % (self._serial.rtscts and 'active' or 'inactive'))
        sys.stderr.write('--- linefeed: %s\n' % (self.LF_MODES[self._convert_outgoing],))
        try:
            sys.stderr.write('--- CTS: %s  DSR: %s  RI: %s  CD: %s\n' % (
                (self._serial.getCTS() and 'active' or 'inactive'),
                (self._serial.getDSR() and 'active' or 'inactive'),
                (self._serial.getRI() and 'active' or 'inactive'),
                (self._serial.getCD() and 'active' or 'inactive'),
                ))
        except serial.SerialException:
            # on RFC 2217 ports it can happen to no modem state notification was
            # yet received. ignore this error.
            pass

    def _reader(self):
        """loop in a separate thread and pull off serial information"""
        try:
            while self._alive:
                data = self._serial.read(1)
                for character in data:
                    #sys.stdout.write("\nrecieved: %s \n" % character.encode('hex'))
                    #only check for XON/XOFF if that is asked for
                    if self._serial.xonxoff:
                        if (character == serial.XON):
                            self._paused = False
                            if self._interface:
                                self._interface.serial_paused()
                        if (character == serial.XOFF):
                            self._paused = True
                            if self._interface:
                                self._interface.serial_resumed()
        except serial.SerialException, e:
            self._alive = False
            # would be nice if the console reader could be interrupted at this
            # point...
            raise

    def write(self, line):
        #if self._paused: 
        #    raise "Cannot write to the serial device, it is paused."
        #if not self._alive: 
        #    raise "Cannot write to the serial device, it is paused."
        self._serial.write(line.strip() + self._newline)

    def flush(self):
        #if self._paused: 
        #    raise "Cannot write to the serial device, it is paused."
        #if not self._alive: 
        #    raise "Cannot write to the serial device, it is paused."
        self._serial.flush()

    def setDTR(self, dtr_state):
        self._serial.setDTR(dtr_state)

    def setRTS(self, rts_state):
        self._serial.setRTS(rts_state)

    def paused(self):
        return self._paused

"""
This class encapsulates the actual command line interface.  It is sent events via method calls
from the serial sending program, and sends signals back, via setting instance variable flags.

This basic interface can be used to implement other user interfaces to the serial sending process.
"""
class CLInterface:
    def __init__(self, debug = False):
        self._current_line = 0
        self._line_count = 0
        self._bar_width = 50
        self._debug = debug
        self._showing_paused = False

    def set_serialterm(self, serialterm):
        self._serialterm = serialterm

    def start(self):
        # start the thread to manage the console UI
        self._alive = True
        self._paused = False
        self._serial_paused = False
        self._stop_requested = False
        # start UI thread
        self._ui_thread = threading.Thread(target=self._reader)
        self._ui_thread.setDaemon(1)
        self._ui_thread.start()
        self._prog = ProgressBar(self._current_line, self._line_count, self._bar_width )
        print "Welcome to the pydnc command line interface."
        print "Press any key to pause the transfer."

    def stop(self):
        if (not self._stop_requested):
            self.update_status("The file transfer completed successfully")
        else:
            self.update_status("The file transfer was terminated before it was fully complete")
        self._alive = False

    def join(self):
        self._ui_thread.join()

    """
    A method that is run as a thread to watch the keyboard
    """
    def _reader(self):
        """loop in a separate thread and watch for console input"""
        while self._alive and not self._stop_requested:
            if (console.keypressed()):
                # the user pressed a key
                # get and handle the pressed key
                c = console.getkey()
                if not self._paused:
                    self._paused = True
                else:
                    if (c == 'Q' or c =='q' or c =='\x03'):
                        print 'File transfer manually terminated before completion at line ' + str(self._current_line) + '.'
                        # this flag signals that the rest of the application should stop
                        self._stop_requested = True
                    else:
                        self._paused = False
                        print 'File transfer resumed due to user key press.'
            #wait between key checks
            time.sleep(0.1)

    """
    This sends a line to the underlying serial terminal
    """
    def send_line(self, line):
        while self.is_paused():
            if not self._showing_paused:
                self._showing_paused = True
                if self._paused:
                    print '\nUser-initiated pause at line.  Press any key to continue sending or q or Q to quit'
                if self._serial_paused:                
                    self.update_status("The file sending process is waiting on the serial port") 
            if self._stop_requested:
                return
            time.sleep(1)
        self._showing_paused = False
        self._current_line = self._current_line + 1
        self._serialterm.write(line)
        self._serialterm.flush()
        self._update_progress()

    """
    This method updates the status bar.
    """
    def _update_progress(self):
        oldprog = str(self._prog)
        # when in debug mode, do not show the progress bar
        if not self._debug:
            self._prog.update_amount(self._current_line)
            if oldprog != str(self._prog):
                print self._prog, "\r",
                sys.stdout.flush()
                oldprog=str(self._prog)

    """
    This method serves to update the current status of the transfer
    """
    def update_status(self, status):
        print("\n" + status)

    """ This method should be called if the serial port is not able to receive data
    """
    def serial_paused(self):
        # if already paused, do nothing
        if not self._serial_paused:
            self._serial_paused = True
 
    """ This method should be called if the serial port once the serial port 
        is able to receive data 
    """
    def serial_resumed(self):
        if self._serial_paused:
        # if already resumed, ignore
            self._serial_paused = False
            if self._paused:
                # handle the case where a user initiated a pause during a serial pause
                print("The serial port is now ready for more data") 
                print('Still paused at line ' + str(self._current_line) + ' of ' + str(self._line_count) + ' due to user key press.  Press any key to continue sending or q or Q to quit')
            else:
                print("The serial port is now ready for more data") 

    def is_paused(self):
        return self._paused or self._serial_paused

    def set_line_count(self, count):
        self._line_count = count

    def stop_requested(self):
        return self._stop_requested

"""
A method to parse the arguments from the command line
"""
def parse_args(arguments, defaults):
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options]",
        description = "pydnc - A simple serial file sending program."
    )

    parser.add_option("-p", "--port",
        dest = "port",
        help = "port, a com port number (default 0)",
        default = defaults['port']
    )

    parser.add_option("-b", "--baud",
        dest = "baudrate",
        action = "store",
        type = 'int',
        help = "set baud rate, default %default",
        default = defaults['baudrate']
    )

    parser.add_option("--parity",
        dest = "parity",
        action = "store",
        help = "set parity, one of [N, E, O, S, M], default=%default",
        default = defaults['parity']
    )

    parser.add_option("--databits",
        dest = "databits",
        action = "store",
        type = 'int',
        help = "set databits, one of [5, 6, 7, 8], default=%default",
        default = defaults['databits']
    )

    parser.add_option("--rtscts",
        dest = "rtscts",
        action = "store_true",
        help = "enable RTS/CTS flow control (default %default)",
        default = defaults['rtscts']
    )

    parser.add_option("--xonxoff",
        dest = "xonxoff",
        action = "store_true",
        help = "enable software flow control (default %default)",
        default = defaults['xonxoff']
    )

    parser.add_option("--cr",
        dest = "cr",
        action = "store_true",
        help = "do not send CR+LF, send CR only (default %default)",
        default = defaults['cr']
    )

    parser.add_option("--lf",
        dest = "lf",
        action = "store_true",
        help = "do not send CR+LF, send LF only (default %default)",
        default = defaults['lf']
    )

    parser.add_option("--rts",
        dest = "rts_state",
        action = "store",
        help = "set initial RTS line state (possible values: 0, 1) (default %default)",
        default = defaults['rts_state']
    )

    parser.add_option("--dtr",
        dest = "dtr_state",
        action = "store",
        help = "set initial DTR line state (possible values: 0, 1) (default %default)",
        default = defaults['dtr_state']
    )
    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non error messages (default %default)",
        default = defaults['quiet']
    )

    parser.add_option("-f", "--file",
        dest = "file_name",
        action = "store",
        help = "the name of the file to send (default %default)",
        default = defaults['file_name']
    )

    (options, args) = parser.parse_args(arguments)

    if args:
        parser.error("No extra arguments allowed when running this script")

    options.parity = options.parity.upper()

    if options.file_name == None:
        parser.error("you must specify a file")

    if options.parity not in 'NEOSM':
        parser.error("invalid parity")

    if options.databits < 5 or options.databits > 8:
        parser.error("invalid databits")
        
    if options.cr and options.lf:
        parser.error("only one of --cr or --lf can be specified")

    options.convert_outgoing = SerialTerm.CONVERT_CRLF
    if options.cr:
        options.convert_outgoing = SerialTerm.CONVERT_CR
    elif options.lf:
        options.convert_outgoing = SerialTerm.CONVERT_LF

    return options

""" This method provides a mechanism to set the defaults for the program.
"""
def get_defaults():
    import ConfigParser
    
    defaults = {
        'file_name': None,
        'baudrate': 9600, 
        'parity': 'E', 
        'databits': 7, 
        'quiet': False, 
        'xonxoff': True, 
        'rtscts': False, 
        'cr': False, 
        'lf': False, 
        'port': 0, 
        'dtr_state': None, 
        'rts_state': None
    }
    option_file_name = 'pydnc-options.ini'
    if os.path.exists(option_file_name):
        print("reading ini file for configuration: " + option_file_name)
        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.read(option_file_name)
        if config.has_option('serial', 'file_name'):
            defaults['file_name'] = config.get('serial', 'file_name')
        if config.has_option('serial', 'baudrate'):
            defaults['baudrate'] = config.getint('serial', 'baudrate')
        if config.has_option('serial', 'parity'):
            defaults['parity'] = config.get('serial', 'parity')
        if config.has_option('serial', 'databits'):
            defaults['databits'] = config.get('serial', 'databits')
        if config.has_option('serial', 'quiet'):
            defaults['quiet'] = config.getboolean('serial', 'quiet')
        if config.has_option('serial', 'xonxoff'):
            defaults['xonxoff'] = config.getboolean('serial', 'xonxoff')
        if config.has_option('serial', 'rtscts'):
            defaults['rtscts'] = config.getboolean('serial', 'rtscts')
        if config.has_option('serial', 'cr'):
            defaults['cr'] = config.getboolean('serial', 'cr')
        if config.has_option('serial', 'lf'):
            defaults['lf'] = config.getboolean('serial', 'lf')
        if config.has_option('serial', 'port'):
            defaults['port'] = config.getint('serial', 'port')
        if config.has_option('serial', 'dtr_state'):
            defaults['dtr_state'] = config.get('serial', 'dtr_state')
        if config.has_option('serial', 'rts_state'):
            defaults['rts_state'] = config.get('serial', 'rts_state')
    else:
    # otherwise, try to create one with default values and write it
        print("An ini file does not exist, attempting to create one: " + option_file_name)
        optionsfile = open (option_file_name, 'wb')
        config = ConfigParser.ConfigParser(allow_no_value=True)
        config.add_section("serial")
        for option in defaults.keys():
            config.set("serial", option, defaults[option])
        config.write(optionsfile)
    return defaults

""" A simple method to return the length of a file given the name
"""
def file_len(fname):
    f = open(fname)
    for i, l in enumerate(f):
        pass
    return i + 1

"""
A simple class to test-drive the command-line user interface
"""
def main():
    # get the default options
    defaults = get_defaults()
    # override with arguments from the command line
    options = parse_args(sys.argv[1:], defaults)

    line_count = file_len(options.file_name)
    
    interface = CLInterface(False)

    interface.set_line_count(line_count)
    interface.start()
    serialterm = SerialTerm(
        options.port,
        options.baudrate,
        bytesize = options.databits,
        parity = options.parity,
        rtscts = options.rtscts,
        xonxoff = options.xonxoff,
        convert_outgoing = options.convert_outgoing,
        interface = interface
    )
    interface.set_serialterm(serialterm)
    serialterm.start()

    input_file = open(options.file_name, "r")

    interface.update_status("The file transfer is beginning.")
    for line in input_file:
        if interface.stop_requested():
            break
        interface.send_line(line)

    serialterm.stop()      
    serialterm.join()
    interface.stop()
    interface.join()
 
if __name__ == '__main__':
    main()

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
"""

import sys, os, threading     
import time, serial

import sys,os

# first choose a platform dependant way to read single characters from the console
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
    import termios, sys, os
    class Console:
        def __init__(self):
            self.fd = sys.stdin.fileno()

        def setup(self):
            self.old = termios.tcgetattr(self.fd)
            new = termios.tcgetattr(self.fd)
            new[3] = new[3] & ~termios.ICANON & ~termios.ECHO & ~termios.ISIG
            new[6][termios.VMIN] = 1
            new[6][termios.VTIME] = 0
            termios.tcsetattr(self.fd, termios.TCSANOW, new)

        def getkey(self):
            c = os.read(self.fd, 1)
            return c

        def cleanup(self):
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old)

        def keypressed(self):
            #not implemented yet
            raise Exception("Not yet implemented")
            
    console = Console()

    def cleanup_console():
        console.cleanup()

    console.setup()
    sys.exitfunc = cleanup_console      #terminal modes have to be restored on exit...

else:
    raise "Sorry no implementation for your platform (%s) available." % sys.platform

CONVERT_CRLF = 2
CONVERT_CR   = 1
CONVERT_LF   = 0
NEWLINE_CONVERISON_MAP = ('\n', '\r', '\r\n')
LF_MODES = ('LF', 'CR', 'CR/LF')

REPR_MODES = ('raw', 'some control', 'all control', 'hex')

class SerialTerm:
    def __init__(self, port, baudrate, parity, rtscts, xonxoff, echo=False, convert_outgoing=CONVERT_CRLF, repr_mode=0):
        try:
            self.serial = serial.serial_for_url(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        except AttributeError:
            # happens when the installed pyserial is older than 2.5. use the
            # Serial class directly then.
            self.serial = serial.Serial(port, baudrate, parity=parity, rtscts=rtscts, xonxoff=xonxoff, timeout=1)
        self.echo = echo
        self.repr_mode = repr_mode
        self.convert_outgoing = convert_outgoing
        self.newline = NEWLINE_CONVERISON_MAP[self.convert_outgoing]
        self.dtr_state = True
        self.rts_state = True
        self.break_state = False

    def start(self):
        self.alive = True
        # start serial->console thread
        self.receiver_thread = threading.Thread(target=self.reader)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()

    def stop(self):
        self.alive = False

    def join(self, transmit_only=False):
        if not transmit_only:
            self.receiver_thread.join()

    def dump_port_settings(self):
        sys.stderr.write("Serial settings: %s  %s,%s,%s,%s\n" % (
            self.serial.portstr,
            self.serial.baudrate,
            self.serial.bytesize,
            self.serial.parity,
            self.serial.stopbits,
        ))
        sys.stderr.write('--- RTS %s\n' % (self.rts_state and 'active' or 'inactive'))
        sys.stderr.write('--- DTR %s\n' % (self.dtr_state and 'active' or 'inactive'))
        sys.stderr.write('--- BREAK %s\n' % (self.break_state and 'active' or 'inactive'))
        sys.stderr.write('--- software flow control %s\n' % (self.serial.xonxoff and 'active' or 'inactive'))
        sys.stderr.write('--- hardware flow control %s\n' % (self.serial.rtscts and 'active' or 'inactive'))
        sys.stderr.write('--- data escaping: %s\n' % (REPR_MODES[self.repr_mode],))
        sys.stderr.write('--- linefeed: %s\n' % (LF_MODES[self.convert_outgoing],))
        try:
            sys.stderr.write('--- CTS: %s  DSR: %s  RI: %s  CD: %s\n' % (
                (self.serial.getCTS() and 'active' or 'inactive'),
                (self.serial.getDSR() and 'active' or 'inactive'),
                (self.serial.getRI() and 'active' or 'inactive'),
                (self.serial.getCD() and 'active' or 'inactive'),
                ))
        except serial.SerialException:
            # on RFC 2217 ports it can happen to no modem state notification was
            # yet received. ignore this error.
            pass

    def reader(self):
        """loop in a separate thread and pull off serial information"""
        try:
            while self.alive:
                data = self.serial.read(1)

                if self.repr_mode == 0:
                    # direct output, just have to care about newline setting
                    if data == '\r' and self.convert_outgoing == CONVERT_CR:
                        sys.stdout.write('\n')
                    else:
                        sys.stdout.write(data)
                elif self.repr_mode == 1:
                    # escape non-printable, let pass newlines
                    if self.convert_outgoing == CONVERT_CRLF and data in '\r\n':
                        if data == '\n':
                            sys.stdout.write('\n')
                        elif data == '\r':
                            pass
                    elif data == '\n' and self.convert_outgoing == CONVERT_LF:
                        sys.stdout.write('\n')
                    elif data == '\r' and self.convert_outgoing == CONVERT_CR:
                        sys.stdout.write('\n')
                    else:
                        sys.stdout.write(repr(data)[1:-1])
                elif self.repr_mode == 2:
                    # escape all non-printable, including newline
                    sys.stdout.write(repr(data)[1:-1])
                elif self.repr_mode == 3:
                    # escape everything (hexdump)
                    for character in data:
                        sys.stdout.write("%s " % character.encode('hex'))
                sys.stdout.flush()
        except serial.SerialException, e:
            self.alive = False
            # would be nice if the console reader could be interruptted at this
            # point...
            raise
 
class ProgressBar:
    def __init__(self, min_value = 0, max_value = 100, width=77,**kwargs):
        self.char = kwargs.get('char', '#')
        self.mode = kwargs.get('mode', 'dynamic') # fixed or dynamic
        if not self.mode in ['fixed', 'dynamic']:
            self.mode = 'fixed'
 
        self.bar = ''
        self.min = min_value
        self.max = max_value
        self.span = max_value - min_value
        self.width = width
        self.amount = 0       # When amount == max, we are 100% done 
        self.update_amount(0) 
 
 
    def increment_amount(self, add_amount = 1):
        """
        Increment self.amount by 'add_ammount' or default to incrementing
        by 1, and then rebuild the bar string. 
        """
        new_amount = self.amount + add_amount
        if new_amount < self.min: new_amount = self.min
        if new_amount > self.max: new_amount = self.max
        self.amount = new_amount
        self.build_bar()
 
 
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
        Figure new percent complete, and rebuild the bar string base on 
        self.amount.
        """
        diff = float(self.amount - self.min)
        percent_done = int(round((diff / float(self.span)) * 100.0))
 
        # figure the proper number of 'character' make up the bar 
        all_full = self.width - 2
        num_hashes = int(round((percent_done * all_full) / 100))
 
        if self.mode == 'dynamic':
            # build a progress bar with self.char (to create a dynamic bar
            # where the percent string moves along with the bar progress.
            self.bar = self.char * num_hashes
        else:
            # build a progress bar with self.char and spaces (to create a 
            # fixe bar (the percent string doesn't move)
            self.bar = self.char * num_hashes + ' ' * (all_full-num_hashes)
 
        percent_str = str(percent_done) + "%"
        self.bar = '[ ' + self.bar + ' ] ' + percent_str
 
 
    def __str__(self):
        return str(self.bar)
 

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
 
def main():
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "pydnc - A simple serial file sending program."
    )

    parser.add_option("-p", "--port",
        dest = "port",
        help = "port, a number (default 0) or a device name (deprecated option)",
        default = None
    )

    parser.add_option("-b", "--baud",
        dest = "baudrate",
        action = "store",
        type = 'int',
        help = "set baud rate, default %default",
        default = 9600
    )

    parser.add_option("--parity",
        dest = "parity",
        action = "store",
        help = "set parity, one of [N, E, O, S, M], default=N",
        default = 'E'
    )

    parser.add_option("-e", "--echo",
        dest = "echo",
        action = "store_true",
        help = "enable local echo (default off)",
        default = False
    )

    parser.add_option("--rtscts",
        dest = "rtscts",
        action = "store_true",
        help = "enable RTS/CTS flow control (default off)",
        default = False
    )

    parser.add_option("--xonxoff",
        dest = "xonxoff",
        action = "store_true",
        help = "enable software flow control (default off)",
        default = False
    )

    parser.add_option("--cr",
        dest = "cr",
        action = "store_true",
        help = "do not send CR+LF, send CR only",
        default = False
    )

    parser.add_option("--lf",
        dest = "lf",
        action = "store_true",
        help = "do not send CR+LF, send LF only",
        default = False
    )

    parser.add_option("-D", "--debug",
        dest = "repr_mode",
        action = "count",
        help = """debug received data (escape non-printable chars)
--debug can be given multiple times:
0: just print what is received
1: escape non-printable characters, do newlines as unusual
2: escape non-printable characters, newlines too
3: hex dump everything""",
        default = 0
    )
    
    parser.add_option("--rts",
        dest = "rts_state",
        action = "store",
        type = 'int',
        help = "set initial RTS line state (possible values: 0, 1)",
        default = None
    )

    parser.add_option("--dtr",
        dest = "dtr_state",
        action = "store",
        type = 'int',
        help = "set initial DTR line state (possible values: 0, 1)",
        default = None
    )
    parser.add_option("-q", "--quiet",
        dest = "quiet",
        action = "store_true",
        help = "suppress non error messages",
        default = False
    )

    parser.add_option("-f", "--file",
        dest = "file_name",
        action = "store",
        help = "the name of the file to send",
        default = None
    )

    (options, args) = parser.parse_args()

    options.parity = options.parity.upper()

    if options.file_name == None:
        parser.error("you must specify a file")
    input_filename = options.file_name

    if options.parity not in 'NEOSM':
        parser.error("invalid parity")

    if options.cr and options.lf:
        parser.error("only one of --cr or --lf can be specified")

    port = options.port
    baudrate = options.baudrate
    if args:
        if options.port is not None:
            parser.error("no arguments are allowed, options only when --port is given")
        port = args.pop(0)
        if args:
            try:
                baudrate = int(args[0])
            except ValueError:
                parser.error("baud rate must be a number, not %r" % args[0])
            args.pop(0)
        if args:
            parser.error("too many arguments")
    else:
        if port is None: port = 0

    convert_outgoing = CONVERT_CRLF
    if options.cr:
        convert_outgoing = CONVERT_CR
    elif options.lf:
        convert_outgoing = CONVERT_LF

    try:
        serialterm = SerialTerm(
            port,
            baudrate,
            options.parity,
            rtscts=options.rtscts,
            xonxoff=options.xonxoff,
            echo=options.echo,
            convert_outgoing=convert_outgoing,
            repr_mode=options.repr_mode,
        )
    except serial.SerialException, e:
        sys.stderr.write("could not open port %r: %s\n" % (port, e))
        sys.exit(1)
        
    if options.dtr_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing DTR %s\n' % (options.dtr_state and 'active' or 'inactive'))
        serialterm.serial.setDTR(options.dtr_state)
        serialterm.dtr_state = options.dtr_state
    if options.rts_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing RTS %s\n' % (options.rts_state and 'active' or 'inactive'))
        serialterm.serial.setRTS(options.rts_state)
        serialterm.rts_state = options.rts_state

    if not options.quiet:
        serialterm.dump_port_settings()

    serialterm.start()
     
    line_count = file_len(input_filename)

    input_file = open(input_filename, "r")

    print 'Filename: ' + input_filename
    print 'total lines: ' + str(line_count)
    print 'Serial file transfer status (press any key to pause):'
    prog = ProgressBar(0, line_count, 60, mode='fixed', char='=')
    oldprog = str(prog)
    current_line = 0
    for line in input_file:
        current_line += 1
        #self.serial.write(self.newline)
        if (options.echo):
            # debug mode, print each line
            sys.stdout.write("%.8d %s" % (current_line, line))
        else:
            # non-debug mode, print a status bar
            prog.increment_amount()
            if oldprog != str(prog):
                print prog, "\r",
                sys.stdout.flush()
                oldprog=str(prog)
        if (console.keypressed()):
            # the user pressed a key to pause
            # clear the current key
            console.getkey()
            print '\nPaused at line ' + str(current_line) + ' of ' + str(line_count) + '. press any key to continue sending or q or Q to quit'
            c = console.getkey()
            if (c == 'Q' or c =='q'):
                print '\nFile transfer manually terminated before completion at line ' + str(current_line) + '.'
                break
        #make it go slow for testing
        time.sleep(0.1)

    print '\nSerial transfer completed.'
        
    input_file.close()
    serialterm.stop()      
    serialterm.join(True)

 
if __name__ == '__main__':
    main()

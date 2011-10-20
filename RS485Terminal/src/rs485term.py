#!/usr/bin/env python

# Very simple serial terminal
# (C)2002-2009 Chris Liechti <cliechti@gmx.net>

# Input characters are sent directly (only LF -> CR/LF/CRLF translation is
# done), received characters are displayed as is (or escaped trough pythons
# repr, useful for debug purposes)


import sys, os, serial, threading, time

def key_description(character):
    """generate a readable description for a key"""
    ascii_code = ord(character)
    if ascii_code < 32:
        return 'Ctrl+%c' % (ord('@') + ascii_code)
    else:
        return repr(character)

# help text, starts with blank line! it's a function so that the current values
# for the shortcut keys is used and not the value at program start
def get_help_text():
    return """
--- pySerial (%(version)s) - rs485term - help
---
--- %(exit)-8s Exit program
--- %(menu)-8s Menu escape key, followed by:
--- Menu keys:
---       %(itself)-8s Send the menu character itself to remote
---       %(exchar)-8s Send the exit character to remote
---       %(info)-8s Show info
---       %(upload)-8s Upload file (prompt will be shown)
--- Toggles:
---       %(rts)s  RTS          %(echo)s  local echo
---       %(dtr)s  DTR          %(break)s  BREAK
---       %(lfm)s  line feed    %(repr)s  Cycle repr mode
---
--- Port settings (%(menu)s followed by the following):
--- 7 8           set data bits
--- n e o s m     change parity (None, Even, Odd, Space, Mark)
--- 1 2 3         set stop bits (1, 2, 1.5)
--- b             change baud rate
--- x X           disable/enable software flow control
--- r R           disable/enable hardware flow control
""" % {
    'version': getattr(serial, 'VERSION', 'unknown'),
    'rts': key_description('\x12'),
    'repr': key_description('\x01'),
    'dtr': key_description('\x04'),
    'lfm': key_description('\x0c'),
    'break': key_description('\x02'),
    'echo': key_description('\x05'),
    'info': key_description('\x09'),
    'upload': key_description('\x15'),
}

"""
Computes the RS485 checksum per the DriveBlok user manual.
"""
def compute_checksum(command):
    sum = 0
    for c in command:
        sum = sum + ord(c)
    #print "binary sum: " + bin(sum)
    sum = sum & 0x7F
    #print "binary sum: " + bin(sum)
    sum = sum | 0x40
    #print chr(sum)
    return chr(sum)
    
def generate_command(command):
    command = command.rstrip()
    command = command.rstrip('\r')
    return command + compute_checksum(command)

def dump_bits(data):
    print "data as bits: ",
    for c in data:
        print "01234567",
    print
    print "bit data    : ",
    for c in data:
        bits = bin(ord(c))[2:]
        print bits.zfill(8),
    print

def dump_hex(data):
    print "data as hex :  ",
    for c in data:
        print hex(ord(c)),
    print

def dump_ascii(data):
    print "data as ASCII :  ",
    for c in data:
        print c,
    print

def dump_dec(data):
    print "data as decimal :  ",
    for c in data:
        print ord(c),
    print
    
def dump_output(command):
    #remove trailing newline if it exists
    command = command.rstrip('\n')
    checksum = command[-1]
    cmd_char = command[0]
    address = command[1]
    data = command[2:-1]
    
    print "******* beginning command output dump *********"
    print "command : " + command
    print "cmd char: " + cmd_char
    print "address : " + address
    print "data    : " + data
    print "checksum: " + checksum
    
    dump_bits(data)
    dump_hex(data)
    dump_ascii(data)
    dump_dec(data)
    
    computed_checksum = compute_checksum(cmd_char + address + data)
    
    if (computed_checksum == checksum):
        print "Checksum is valid"
    else:
        print "Checksum is INVALID! (expected \"" + computed_checksum + "\")"
    print "******* finished command output dump **********"


CONVERT_CRLF = 2
CONVERT_CR   = 1
CONVERT_LF   = 0
NEWLINE_CONVERISON_MAP = ('\n', '\r', '\r\n')
LF_MODES = ('LF', 'CR', 'CR/LF')

REPR_MODES = ('raw', 'some control', 'all control', 'hex')

class RS485Term:
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
        # enter console->serial loop
        self.transmitter_thread = threading.Thread(target=self.writer)
        self.transmitter_thread.setDaemon(1)
        self.transmitter_thread.start()

    def stop(self):
        self.alive = False

    def join(self, transmit_only=False):
        self.transmitter_thread.join()
        if not transmit_only:
            self.receiver_thread.join()

    def dump_port_settings(self):
        sys.stderr.write("\n--- Settings: %s  %s,%s,%s,%s\n" % (
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
        """loop and copy serial->console, decoding full commands"""
        try:
            r_cmd = ""
            while self.alive:
                data = self.serial.read(1)

                for character in data:
                    if character == '\r':
                        dump_output(r_cmd)
                        r_cmd = ""
                    else:
                        r_cmd = r_cmd + data
        except serial.SerialException, e:
            self.alive = False
            # would be nice if the console reader could be interruptted at this
            # point...
            raise


    def writer(self):
        """loop and copy console->serial until EXITCHARCTER character is
           found. when MENUCHARACTER is found, interpret the next key
           locally.
        """
        try:
            while self.alive:
                print "> ", #the prompt
                input = sys.stdin.readline()
                input = input.rstrip()
                if (input == "exit" or input == "quit"):
                    self.stop()
                    break
                command = generate_command(input)
                print
                for c in command:
                    if c == '\n':
                        self.serial.write(self.newline)         # send newline character(s)
                    else:
                        self.serial.write(c)                    # send character
                time.sleep(0.1)
        except:
            self.alive = False
            raise

def main():
    import optparse

    parser = optparse.OptionParser(
        usage = "%prog [options] [port [baudrate]]",
        description = "rs485term - A simple terminal program for the serial port."
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
        default = 'N'
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

    (options, args) = parser.parse_args()

    options.parity = options.parity.upper()
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
        term = RS485Term(
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

    if not options.quiet:
        sys.stderr.write('--- rs485term on %s: %d,%s,%s,%s ---\n' % (
            term.serial.portstr,
            term.serial.baudrate,
            term.serial.bytesize,
            term.serial.parity,
            term.serial.stopbits,
        ))
        sys.stderr.write('--- Quit: exit ---\n' )
        sys.stderr.write('--- Enter an RS485 command such as "$1A00" and press Enter ---\n' )

    if options.dtr_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing DTR %s\n' % (options.dtr_state and 'active' or 'inactive'))
        term.serial.setDTR(options.dtr_state)
        term.dtr_state = options.dtr_state
    if options.rts_state is not None:
        if not options.quiet:
            sys.stderr.write('--- forcing RTS %s\n' % (options.rts_state and 'active' or 'inactive'))
        term.serial.setRTS(options.rts_state)
        term.rts_state = options.rts_state

    term.start()
    term.join(True)
    if not options.quiet:
        sys.stderr.write("\nterminal exiting\n")
    term.join()


if __name__ == '__main__':
    main()

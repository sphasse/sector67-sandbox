#!/usr/bin/env python
"""
A mock serial terminal to facilitate testing serial operations
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

Developed by Scott Hasse for use at http://sector67.org
"""

import sys, os, threading     
import time
import pydnc


class MockSerialTerm:
    CONVERT_CRLF = 2
    CONVERT_CR   = 1
    CONVERT_LF   = 0
    NEWLINE_CONVERISON_MAP = ('\n', '\r', '\r\n')
    LF_MODES = ('LF', 'CR', 'CR/LF')

    REPR_MODES = ('raw', 'some control', 'all control', 'hex')

    def __init__(self, port, baudrate, parity, rtscts, xonxoff, convert_outgoing=CONVERT_CRLF, bytesize=7, interface=None):
        self._convert_outgoing = convert_outgoing
        self._newline = self.NEWLINE_CONVERISON_MAP[self._convert_outgoing]
        self._dtr_state = True
        self._rts_state = True
        self._break_state = False
        self._paused = False
        self._interface = interface

    def start(self):
        self._alive = True
        # start serial->console thread
        self._receiver_thread = threading.Thread(target=self._reader)
        self._receiver_thread.setDaemon(1)
        self._receiver_thread.start()
        self._output_file = open("mock-serial-out.txt", "wb")

    def stop(self):
        self._alive = False
        self._output_file.close()

    def join(self):
        self._receiver_thread.join()

    def dump_port_settings(self):
        sys.stderr.write('This is a mock serial port')

    def _reader(self):
        """loop in a separate thread and pause and unpause"""
        while self._alive:
            self._paused = False
            if self._interface:
                self._interface.serial_resumed()
            time.sleep(4)
            self._paused = True
            if self._interface:
                self._interface.serial_paused()
            time.sleep(2)

    def write(self, line):
        self._output_file.write(line.strip() + self._newline)
        #introduce some delay
        time.sleep(0.1)

    def flush(self):
        self._output_file.flush()
        #TODO: make this write to a file
        pass

    def setDTR(self, dtr_state):
        self._dtr_state = dtr_state

    def setRTS(self, rts_state):
        self._rts_state = rts_state

    def paused(self):
        return self._paused


def main():
    line_count = 150
    current_line = 1 
    interface = pydnc.CLInterface(False)
    interface.set_line_count(line_count)
    interface.start()

    serialterm = MockSerialTerm(
        0,
        9600,
        'E',
        False,
        True,
        MockSerialTerm.CONVERT_CRLF,
        7,
        interface
    )
    interface.set_serialterm(serialterm)
    serialterm.start()

    interface.update_status("The file transfer is beginning.")

    while current_line <= line_count:
        if interface.stop_requested():
            break
        mockline = "This is fake line #" + str(current_line) + "\n"
        interface.send_line(mockline)
        current_line = current_line + 1

    serialterm.stop()      
    serialterm.join()
    interface.stop()
    interface.join()
 
if __name__ == '__main__':
    main()

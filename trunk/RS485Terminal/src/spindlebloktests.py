'''
Created on Nov 29, 2010

@author: shasse
'''
import unittest
import spindleblokutils
from spindleblokutils import DataUtils
from spindleblokutils import MockCommandChannel
from spindleblokutils import RS485Command
import re, time

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_apply_or_bit_mask(self):
        self.assertEqual("ffff", DataUtils.apply_or_bit_mask("ffff", "0000"))
        self.assertEqual("ffff", DataUtils.apply_or_bit_mask("FFFF", "0000"))
        self.assertEqual("ffff", DataUtils.apply_or_bit_mask("fFfF", "0000"))
        self.assertEqual("abcd", DataUtils.apply_or_bit_mask("abcd", "abcd"))
        self.assertEqual("ffff", DataUtils.apply_or_bit_mask("aaaa", "5555"))
        self.assertEqual("0fff", DataUtils.apply_or_bit_mask("0aaa", "0555"))
        self.assertEqual("0000", DataUtils.apply_or_bit_mask("0000", "0000"))
        self.assertEqual("00", DataUtils.apply_or_bit_mask("00", "00"))

    def test_signed_ints(self):
        self.assertEqual(1, DataUtils.hex_string_to__signed_int("0001"))
        self.assertEqual(-1, DataUtils.hex_string_to__signed_int("ffff"))
        self.assertEqual(-32768, DataUtils.hex_string_to__signed_int("8000"))
        self.assertEqual(-32767, DataUtils.hex_string_to__signed_int("8001"))
        self.assertEqual(32767, DataUtils.hex_string_to__signed_int("7fff"))

        self.assertEqual("0001", DataUtils.signed_int_to_hex_string(1, 16))
        self.assertEqual("ffff", DataUtils.signed_int_to_hex_string(-1, 16))
        self.assertEqual("8001", DataUtils.signed_int_to_hex_string(-32767, 16))
        self.assertEqual("8000", DataUtils.signed_int_to_hex_string(-32768, 16))
        
        # test the inverse functions actually invert
        for i in range(0,(2**16)):
            hexString = "%0.4x" % i
            self.assertEqual(hexString, DataUtils.signed_int_to_hex_string(DataUtils.hex_string_to__signed_int(hexString), 16))
        
    def test_mock_channel(self):
    
        mock_channel = MockCommandChannel()
        mock_channel.start()
        request = RS485Command.create_outgoing_command("$", "1", "C00", "ffff")
        # put a command
        mock_channel.send_command(request)
        # wait for the reply
        reply = mock_channel.receive_reply(1)
        self.assertEqual("$1C00ffffc", reply.full_string)

        request = RS485Command.create_outgoing_command("$", "1", "C01", "ffff")
        mock_channel.send_command(request)
        reply = mock_channel.receive_reply(1)
        self.assertEqual("$1C01ffffd", reply.full_string)

        mock_channel.stop()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
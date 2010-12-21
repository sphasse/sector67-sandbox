'''
Created on Nov 29, 2010

@author: shasse
'''
import unittest
import anilampost

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_parse_gcode(self):
        self.assertEqual(["G0", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("/N123 G00 X1.00 Y1.00 (comment) Z.123"))
        self.assertEqual(["G0", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("/N123 G00 X1.00 y1.00 (comment) Z.123"))
        self.assertEqual(["G0", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("N123 G00 X1.00 y1.00 (comment) Z.123"))
        self.assertEqual(["G0", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("G00 X1.00 y1.00 Z.123"))
        self.assertEqual(["G0", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("G00 X1.00 (first inline comment) y1.00 Z.123 (second inline comment)"))
        self.assertEqual(["G1"], anilampost.parse_gcode("G01"))
        self.assertEqual(["G0"], anilampost.parse_gcode("G00"))
        self.assertEqual(["G0"], anilampost.parse_gcode("G000"))
        self.assertEqual(["G17"], anilampost.parse_gcode("G017"))
        self.assertEqual(["G0", "X.123"], anilampost.parse_gcode("G0X0.123"))
        pass
    
    def test_real_part(self):
        self.assertEqual("123.0", anilampost.real_part("G123.0"))
        self.assertEqual("10", anilampost.real_part("G10"))
        self.assertEqual("-.10", anilampost.real_part("G-.10"))
        self.assertEqual("-.10", anilampost.real_part("X-0.10"))
        self.assertEqual("-.10", anilampost.real_part("X-0000.10"))
        self.assertEqual("0", anilampost.real_part("G0000"))
        self.assertEqual("0", anilampost.real_part("G0"))
        self.assertEqual("+.01", anilampost.real_part("X+0.01"))
        pass
    
    def test_command_part(self):
        self.assertEqual("G", anilampost.command_part("G123.0"))
        self.assertEqual("G", anilampost.command_part("G-.10"))
        self.assertEqual("G", anilampost.command_part("G10"))
        pass

    def test_extract_comments(self):
        self.assertEqual(["This is a test"], anilampost.extract_comments("G123.0 (This is a test)"))
        self.assertEqual(["This is a test", "Another inline comment"], anilampost.extract_comments("G123.0 (This is a test) G012 (Another inline comment)"))
        self.assertEqual(["A standalone comment"], anilampost.extract_comments("(A standalone comment)"))
        pass

    def test_convert(self):
        self.assertEqual("RPM        60.0000", anilampost.convert_to_conversational(["S60.0000"], "S60.000"))
        self.assertEqual("* * O123", anilampost.convert_to_conversational(["O123"], "O123"))
        self.assertEqual("Line       Feed 10.0000", anilampost.convert_to_conversational(["G1", "F10"], "G1F10"))
        self.assertEqual("Rapid      Feed 10.0000", anilampost.convert_to_conversational(["G0", "F10"], "G0F10"))
        self.assertEqual("MCode 5", anilampost.convert_to_conversational(["M5"], "M5"))
        self.assertEqual("X 10.0000", anilampost.convert_to_conversational(["X10"], "X10"))
        self.assertEqual("X 10.0000 Y 12.0000", anilampost.convert_to_conversational(["X10", "Y12"], "X10Y12"))
        self.assertEqual("X 10.0000 Feed 12.0000", anilampost.convert_to_conversational(["X10", "F12"], "X10F12"))
        self.assertEqual("Dwell 1.0000", anilampost.convert_to_conversational(["G04", "P1.0"], "G04 P1.0"))
        self.assertEqual("Dwell 1.0000", anilampost.convert_to_conversational(["G04", "P1.0"], "G04 P1.000"))
        self.assertEqual("Tool# 3", anilampost.convert_to_conversational(["T3"], "T3"))
        self.assertEqual("Tool# 4", anilampost.convert_to_conversational(["T4.00"], "T4.00"))

    def test_lines(self):
        self.assertEqual("* * %\n", anilampost.process_line("%\n"))
        self.assertEqual("* * O123\n", anilampost.process_line("O123\n"))
        self.assertEqual("Plane XY\n", anilampost.process_line("G17"))
        self.assertEqual("Plane ZX\n", anilampost.process_line("G18"))
        self.assertEqual("Plane YZ\n", anilampost.process_line("G19"))
        self.assertEqual("Dwell 1.0000\n", anilampost.process_line("G04 P1.0"))
        self.assertEqual("* * ;This line is a comment\n", anilampost.process_line(";This line is a comment\n"))

    
    def test_verify_gcode(self):
        print "\n### This test expects an error to be logged below ############"
        try:
            #G1 and G0 are both move modal
            anilampost.verify_gcode(["G0", "G1"])
            # an exception should be thrown
            self.assertTrue(False)
        except:
            self.assertTrue(True)
        print "##############################################################"

        print "\n### This test expects an error to be logged below ############"
        # This should fail because the G00 will not be parsed properly.  The
        # method requires the commands to be normalized with no leading zeros.
        try:
            anilampost.verify_gcode(["G1000", "G2000"])
            # an exception should be thrown
            self.assertTrue(False)
        except:
            self.assertTrue(True)
        print "##############################################################"
        
        anilampost.verify_gcode(["G0", "M1"])
        
        print "\n### This test expects an error to be logged below ############"
        # This should fail
        try:
            anilampost.verify_gcode(["G1", "X0.0", "X1.0", "Z1.0"])
            # an exception should be thrown
            self.assertTrue(False)
        except:
            self.assertTrue(True)
        print "##############################################################"
        
        #G4 is non-modal, should be fine
        anilampost.verify_gcode(["G0", "G4", "P10"])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
'''
Created on Nov 29, 2010

@author: shasse
'''
import unittest
import anilampost
import re

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
        self.assertEqual("RPM        60.0000", anilampost.convert_to_conversational(["S60.0000"]))
        self.assertEqual("* O123", anilampost.convert_to_conversational(["O123"]))
        self.assertEqual("Line       Feed 10.0000", anilampost.convert_to_conversational(["G1", "F10"]))
        self.assertEqual("Rapid      Feed 10.0000", anilampost.convert_to_conversational(["G0", "F10"]))
        self.assertEqual("MCode 5", anilampost.convert_to_conversational(["M5"], "M5"))
        self.assertEqual("X 10.0000", anilampost.convert_to_conversational(["X10"], "X10"))
        self.assertEqual("X 10.0000 Y 12.0000", anilampost.convert_to_conversational(["X10", "Y12"]))
        self.assertEqual("X 10.0000 Feed 12.0000", anilampost.convert_to_conversational(["X10", "F12"]))
        self.assertEqual("Dwell 1.0000", anilampost.convert_to_conversational(["G04", "P1.0"]))
        self.assertEqual("Dwell 1.0000", anilampost.convert_to_conversational(["G04", "P1.0"]))
        self.assertEqual("Tool# 3", anilampost.convert_to_conversational(["T3"]))
        self.assertEqual("Tool# 4", anilampost.convert_to_conversational(["T4.00"]))
        self.assertEqual("DrillOff", anilampost.convert_to_conversational(["G80"]))
        
    def test_drill(self):
        self.assertEqual("Feed 100.0000\nPeckDrill ZDepth -3.0000 StartHgt 0.1000 Peck 1.0000\n", anilampost.process_line("G83 Z-3.0 R0.1 Q1.0 F100"))
        self.assertEqual("Feed 100.0000\nBasicDrill ZDepth -3.0000 StartHgt 0.1000\n", anilampost.process_line("G81 Z-3.0 R0.1 F100"))
        # The lines below show some additional options but are not implemented
        #self.assertEqual("PeckDrill ZDepth -1.0000 StartHgt 1.0000 Peck 0.2500 Feed 100.0000 ReturnHeight 1.0000", anilampost.convert_to_conversational(["G83", "Z-1.0", "R1.0", "I0.25", "F100", "P1.0"]))
        #self.assertEqual("BasicDrill ZDepth -1.0000 StartHgt 1.0000 Feed 100.0000 ReturnHeight 1.0000", anilampost.convert_to_conversational(["G81", "Z-1.0", "R1.0", "F100", "P1.0"]))

    def test_lines(self):
        self.assertEqual("* %\n", anilampost.process_line("%\n"))
        self.assertEqual("* O123\n", anilampost.process_line("O123\n"))
        self.assertEqual("Plane XY\n", anilampost.process_line("G17\n"))
        self.assertEqual("Plane ZX\n", anilampost.process_line("G18\n"))
        self.assertEqual("Plane YZ\n", anilampost.process_line("G19\n"))
        self.assertEqual("Dwell 1.0000\n", anilampost.process_line("G04 P1.0\n"))
        self.assertEqual("* ;This line is a comment\n", anilampost.process_line(";This line is a comment\n"))
        self.assertEqual("* per --ignore regex, ignored word: G123\nX 1.0000 Y 2.0000\n", anilampost.process_line("G123 X1 Y2\n", -1, "^(G123|G124)$"))
        self.assertEqual("* per --ignore regex, ignored word: G12\nX 1.0000 Y 2.0000\n", anilampost.process_line("G12 X1 Y2\n", -1, "^(G10|G12)$"))
        self.assertEqual("Dwell 2.0000\n", anilampost.process_line("G4 P2\n", -1, "^(G1|G2)$"))
        self.assertEqual("Plane XY\nUnit MM\nDim Abs\n", anilampost.process_line("G90G21G17\n"))

        print "\n### This test expects an error to be logged below ############"        
        try:
	    anilampost.process_line("G123 X1 Y2\n", -1, "^(G10|G12)$")
	    self.assertTrue(False, "This should not be reached")
	except Exception as e:
            self.assertTrue(re.search("Not all modal G words were able to be recognized", str(e)), str(e) + " should match")
        print "##############################################################"

        self.assertEqual("Dwell 10.0000\nRapid      X 1.0000 Y 1.0000 Z 1.0000\n", anilampost.process_line("G0 G4 P10 X1 Y1 Z1"))
        self.assertEqual("Feed 100.0000\nDwell 10.0000\nRapid      X 1.0000 Y 1.0000 Z 1.0000\n", anilampost.process_line("G0 G4 P10 X1 Y1 Z1 F100"))

    
    def test_verify_gcode(self):
        print "\n### This test expects an error to be logged below ############"
        try:
            #G1 and G0 are both move modal
            anilampost.verify_gcode(["G0", "G1"])
            # an exception should be thrown
            self.assertTrue(False, "This should not be reached")
        except Exception as e:
            self.assertTrue(re.search("There were more than 1 axis-using G words in a block.", str(e)), str(e) + " should match")
        print "##############################################################"

        print "\n### This test expects an error to be logged below ############"
        # This should fail because the G00 will not be parsed properly.  The
        # method requires the commands to be normalized with no leading zeros.
        try:
            anilampost.verify_gcode(["G1000", "G2000"])
            # an exception should be thrown
            self.assertTrue(False, "This should not be reached")
        except Exception as e:
            self.assertTrue(re.search("Not all modal G words were able to be recognized", str(e)), str(e) + " should match")
        print "##############################################################"
        
        anilampost.verify_gcode(["G0", "M1"])
        
        print "\n### This test expects an error to be logged below ############"
        # This should fail
        try:
            anilampost.verify_gcode(["G1", "X0.0", "X1.0", "Z1.0"])
            # an exception should be thrown
            self.assertTrue(False, "This should not be reached")
        except Exception as e:
            self.assertTrue(re.search("There were more 1 X words in a block.", str(e)), str(e) + " should match")
        print "##############################################################"
        
        
        print "\n### This test expects an error to be logged below ############"
        # This should fail
        try:
            anilampost.verify_gcode(["G1", "G10", "X0.0", "X1.0", "Z1.0"])
            # an exception should be thrown that there are two 
            self.assertTrue(re.search("There were more than 1 axis-using words in a block.", str(e)), str(e) + " should match")
        except Exception as e:
            self.assertTrue(True)
                    
        print "##############################################################"
        
        #G4 is non-modal, should be fine
        anilampost.verify_gcode(["G0", "G4", "P10", "X1", "Y1", "Z1"])
    
    def test_multiplex_blocks(self):
        self.assertEqual([["G93"],["F100"]], anilampost.multiplex_blocks(["F100", "G93"]))
        self.assertEqual([["S400"],["M6"]], anilampost.multiplex_blocks(["M6", "S400"]))
        self.assertEqual([["F100"], ["G4", "P2"]], anilampost.multiplex_blocks(["G4", "P2", "F100"]))
        self.assertEqual([["F100"], ["G4", "P2"], ["G17"], ["G21"]], anilampost.multiplex_blocks(["G17", "G21", "G4", "P2", "F100"]))
        #self.assertEqual([["F100"], ["G4", "P2"]], anilampost.multiplex_blocks(["G1", "X1", "Y1", "G4", "P2", "F100"]))
        self.assertEqual([["G17"], ["G21"], ["G54"], ["G90"]], anilampost.multiplex_blocks(["G90", "G21", "G17", "G54"]))
        self.assertEqual([["G1", "X1", "Y1", "Z1"]], anilampost.multiplex_blocks(["G1", "X1", "Y1", "Z1"]))
        self.assertEqual([["G1", "G53", "X1", "Y1", "Z1"]], anilampost.multiplex_blocks(["G1", "X1", "Y1", "Z1", "G53"]))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
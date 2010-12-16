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
        self.assertEqual(["N123", "G00", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("/N123 G00 X1.00 Y1.00 (comment) Z.123"))
        self.assertEqual(["N123", "G00", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("/N123 G00 X1.00 y1.00 (comment) Z.123"))
        self.assertEqual(["G00", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("G00 X1.00 y1.00 Z.123"))
        self.assertEqual(["G00", "X1.00", "Y1.00", "Z.123"], anilampost.parse_gcode("G00 X1.00 (first inline comment) y1.00 Z.123 (second inline comment)"))
        pass
    
    def test_real_part(self):
        self.assertEqual("123.0", anilampost.real_part("G123.0"))
        self.assertEqual("10", anilampost.real_part("G10"))
        self.assertEqual("-.10", anilampost.real_part("G-.10"))
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

    def test_lines(self):
        self.assertEqual("* * %\n", anilampost.process_line("%\n", -1))
        self.assertEqual("* * O123\n", anilampost.process_line("O123\n", -1))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
'''
A script to convert GCode to Anilam conversational format.

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

More details on the gcode specification can be found here:

http://www.linuxcnc.org/handbook/gcode/g-code.html

and

http://linuxcnc.org/docs/html/gcode_overview.html

The conversational format can be found partially described at:

http://www.anilam.com/Uploads/File/Training%20Presentation%20PDF%20Files/3000M_Training_2.pdf

and

http://www.anilam.com/Uploads/File/CNC%20Control%20Manuals%20September%202006/3000M/70000504H.pdf

In general since the code generated by this script will ultimately be used to move
a machine, the goal of this script is to accurately translate programs, and
to fail fast and accurately when that cannot be done.  As a result, some of the 
implementation (most notably convert_to_conversational) probably appears to
be implemented in a fairly brittle manner.  This is for the most part intentional.
Each command and variation handled is explicit, and other unknown commands result
in an error.

It is expected this script will have a few primary uses:

1) For converting programs that are larger than the Anilam 1100 can handle.  These
programs will then subsequently be drip fed to the mill.
2) To correctly translate gcode programs that use arcs with IJK coordinates
specified incrementally.  Although incremental IJK specification is the default
in gcode, the Anilam-based translator expects the IJK to be absolute.  Although
this translator is incomplete, it is superior in that respect.
3) To avoid multiple round-trips to the mill with floppy disks.

TODO:
* The gcode verifier could be greatly improved.  However, since the translation
is done rather explicitly, it is hoped this will not introduce any risk to the
translation process.
* Translations for some Anilam functions that have gcode equivalents:

peck drill
tool change

etc. are not implemented
'''

import re
import getopt
import sys
from datetime import datetime

known_gcode_words = "FGIJKMNOPSTXYZ"
log_level = 1
current_coords_mode = "ABS"
current_arc_coords_mode = "INC"

motion_modal_commands = frozenset(["G0", "G1", "G2", "G3", "G80", "G81", "G82", "G83", "G84", "G85", "G86", "G87", "G88", "G89"])
plane_selection_modal_commands = frozenset(["G17", "G18", "G19"])
distance_modal_commands = frozenset(["G90", "G91"])
spindle_speed_modal_commands = frozenset(["G93", "G94"])
units_modal_commands = frozenset(["G20", "G21"])
cutter_diameter_compensation_modal_commands = frozenset(["G40", "G41", "G42"])
tool_length_offset_modal_commands  = frozenset(["G43", "G49"])
return_mode_in_canned_cycles_modal_commands = frozenset(["G98", "G99"])
coordinate_system_selection_modal_commands = frozenset(["G54", "G55", "G56", "G57", "G58", "G59", "G59.1", "G59.2", "G59.3"])

g_modal_groups = [motion_modal_commands, plane_selection_modal_commands, distance_modal_commands, spindle_speed_modal_commands, units_modal_commands, cutter_diameter_compensation_modal_commands, tool_length_offset_modal_commands, return_mode_in_canned_cycles_modal_commands, coordinate_system_selection_modal_commands]

axis_clamping_modal_commands = frozenset(["M26", "M27"]) 
stopping_modal_commands = frozenset(["M0", "M1", "M2", "M30", "M60"])
tool_change_modal_commands  = frozenset(["M6"])
spindle_turning_modal_commands  = frozenset(["M3", "M4", "M5"])
coolant_modal_commands = frozenset(["M7", "M8", "M9"])
feed_and_speed_override_bypass_modal_commands = frozenset(["M48", "M49"])

m_modal_groups = [axis_clamping_modal_commands, stopping_modal_commands, tool_change_modal_commands, spindle_turning_modal_commands, coolant_modal_commands, feed_and_speed_override_bypass_modal_commands]

non_modal_commands = frozenset(["G4", "G10", "G28", "G30", "G53", "G92", "G92.1", "G92.2", "G92.3"])

def error(message):
    print("ERROR: " + message)

def debug(message):
    if (log_level < 1):
        print("DEBUG: " + message)


"""
A method to return the count of a certain type of code words in a block.
This is used to validate the gcode
block_array is an array of gcode words as strings
command is a letter

"""
def count_words(block_array, command):
    word_count = 0
    for word in block_array:
        if (word.startswith(command)):
            word_count = word_count + 1
    return word_count

"""
A method to parse a line (block) of gcode passed as a string into individual words
returns an array of individual gcode words as strings
This method cleans up the gcode in significant ways:
1) comments are stripped
2) whitespace is stripped
3) leading slashes are stripped
4) all letters are capitalized
5) extraneous leading zeros are stripped

"""
def parse_gcode(block, linenum=-1):
    #strip optional leading "/"
    block = re.sub("^/", "", block)
    #strip out all whitespace
    block = re.sub("\s","", block)
    #strip out inline comments, non-greedy
    block = re.sub("\\(.*?\\)", "", block)
    #capitalize all letters
    block = block.upper()
    
    #parse the block into individual words, failing fast if we encounter any unknown gcode words
        
    result = re.findall("[" + known_gcode_words + "][+-]?\d*\.?\d*", block)
    #check that each part of the string was matched, if not, raise an exception
    test_result = ""
    for word in result:
        test_result += word
    if (test_result != block):
        error("I was not able to parse a block of gcode.  When separating the following block using regex:")
        error(block)
        error("I got the following result:")
        error(test_result)
        raise Exception("I was not able to successfully parse the [" + block + "] block of gcode (input file line number: " + str(linenum) + ").")
    
    # strip leading zeros from the result
    # drop N words
    stripped_result = []
    for word in result:
        command = command_part(word)
        if (command not in "N"):
            real = real_part(word)
            stripped_result.append(command + real)
    
    verify_gcode(stripped_result, linenum)
    return stripped_result


'''
Given a block of gcode, returns an array of comments in that block 
'''
def extract_comments(block):
    #strip out inline comments, non-greedy
    result = re.findall("\\((.*?)\\)", block)
    return result

'''
Check for duplicate words from the same modal group
In order to perform efficient set comparison, this method expects that the 
block_array will contain words with commands that have already had extraneous 
leading zeros stripped.  It does, however, check to make sure it has checked
all of the commands for the passed in command letter.  If they have not all
been checked for duplicates (that is, a command did not exist anywhere in any of
the sets in the modal_groups list, it should log an error that all gcode words
could not be checked.

commands from the non_modal_commands are subtracted from the set

block_array is an array of strings containing the individual gcode words
modal_groups is a list of sets of the modal groups commands
command is a single letter prefix of gcode commands (typically, "G" or "M")
'''
def check_for_duplicates(block_array, modal_groups, command, linenum=-1):
    total_words = 0
    #First, subtract out any non-modal words
    modal_words = set(block_array).difference(non_modal_commands)
    word_count = count_words(modal_words, command)
    for modal_group in modal_groups:
        # The & operator returns the set intersection
        intersection = len(modal_group.intersection(modal_words))
        # ensure each word is accounted for in the checks
        total_words = total_words + intersection
        if (intersection > 1):
            error ("There is more than one " + command + " word from the same modal group on input file line " + str(linenum) + ".  The input gcode is not valid.")
            error ("The modal group is: " + str(modal_group))
            error ("The line is: " + str(block_array))
            error ("The line number is: " + str(linenum))

            raise Exception("There is more than one " + command + " word from the same modal group.  The input gcode is not valid.")
    if (word_count != total_words):
        error ("Not all " + command + " words were able to be checked, some were missed.  There must be some unrecognized commands in the line.  Checked " + str(total_words) + " and there were " + str(word_count) + " words in the block")
        error ("The line is: " + str(block_array))
        error ("The line number is: " + str(linenum))
        raise Exception("Not all " + command + " words were able to be checked, some were missed.  There must be some unrecognized commands in the line.  Checked " + str(total_words) + " and there were " + str(word_count) + " words in the block")


"""
A method to multiplex apart a single gcode line containing several different gcode commands into individual lines
suitable for converting into conversational format.

it expects an array of gcode words representing one block and returns array of array of gcode words representing blocks

TODO: Currently not implemented, it is not clear to me the best way to do this
"""
def multiplex_blocks(block):
    return [block]



"""
Verify that the input gcode is valid.
Currently does some checks, but could do more.
"""
def verify_gcode(block_array, linenum=-1):
    # N words only in the first position
    # Check for line too long?
    # TODO: It is an error to put a G-code from group 1 (move) and a G-code from group 0 (non-modal) 
    # on the same line if both of them use axis words. If an axis word-using G-code from group 1 is 
    # implicitly in effect on a line (by having been activated on an earlier line), and a group 0 G-code 
    # that uses axis words appears on the line, the activity of the group 1 G-code is suspended for that 
    # line. The axis word-using G-codes from group 0 are G10, G28, G30, and G92. 


    # A line may have any number of G words.
    # A line may have zero to four M words.
    # For all other legal letters, a line may have only one word beginning with that letter.    
    for letter in known_gcode_words:
        word_count = count_words(block_array, letter)
        limit = 1
        if (letter in "M"):
            limit = 4
        elif (letter in "G"):
            limit = len(g_modal_groups)
        if (word_count > limit):
            error("There were more than " + str(limit) + " " + letter + " words in a block.  The input gcode is invalid.")
            error("Line number: " + str(linenum))
            error("Block: " + str(block_array))
            raise Exception("There were more " + str(limit) + " " + letter + " words in a block.  The input gcode is invalid")
            

    # Two M words from the same modal group may not appear on the same line.
    
    check_for_duplicates(block_array, m_modal_groups, "M", linenum)

    # Two G words from the same modal group may not appear on the same line.
    check_for_duplicates(block_array, g_modal_groups, "G", linenum)
    
    
"""
translate an entire file line-by-line
"""
def translate_file(input_filename, output_filename):
    debug("parsing " + input_filename)
    input_file = open(input_filename, "r")
    debug("sending output to " + output_filename)
    output_file = open(output_filename, "w")
    line_num = 0
    output_file.write("* * Anilam conversational format generated by anilampost.py at " + str(datetime.now()) + "\n")
    output_file.write("* * original file: " + input_filename + "\n")
    output_file.write("\n")
    for line in input_file:
        line_num += 1
        debug("Processing line number: " + str(line_num))
        debug(line)
        result = process_line(line, line_num)
        output_file.write(result)
            
    input_file.close()
    output_file.close()

"""
process an individual line as a string
returns the conversational code as a string
"""
def process_line(line, line_num=-1):
    result = ""
    line_without_comments = re.sub("\\(.*?\\)", "", line)
    if (re.match("^\s*$", line)):
        debug("Processing as a line with only whitespace")
        result = "\n"
    elif (re.match("^\s*%\s*$", line_without_comments)):
        debug("Processig as a standalone % designating program start or end")
        result = "* * %\n"
    elif (re.match("^;", line)):
        #The line starts with a semicolon, it is a comment
        debug("Processing as a comment line")
        result = result + "* * " + line
    elif (re.match("^\s*$", line_without_comments)):
        #The line is comments and white space only
        #Extract the comments and print them
        debug("Processing as a line with comments and whitespace only")
        comments = extract_comments(line)
        for comment in comments:
            result = result + "* * " + comment + "\n"
    else:
        #The block is gcode and might contain comments
        debug("Processing as a line with gcode and optionally comments")
        #First, extract in-line comments
        if (log_level < 1):
            # in debug mode, write the original line in-line
            result = result + "* * " + line
        comments = extract_comments(line)
        for comment in comments:
            result = result + "* * inline comment: " + comment + "\n"
        #might need to multiplex one line of commands into multiple lines

        block = parse_gcode(line, line_num)
        multiplexed_blocks = multiplex_blocks(block)
        for multiplexed_block in multiplexed_blocks:
            #Then, convert each line
            conversational = convert_to_conversational(multiplexed_block, line, line_num)
            result = result + conversational + "\n"
        
    return result


"""
Given a gcode word as a string, returns the command part of it
"""
def command_part(word):
    command_part = word[0]
    if (re.match("[" + known_gcode_words + "]",command_part)) :
        return command_part
    else:
        raise Exception("Uknown gcode command part: " + command_part + " in word [" + word + "]")

"""
Given a gcode word as a string, returns the real_number part of it
extraneous leading zeros are stripped
"""
def real_part(word):
    real_part = word[1:]
    stripped_real_part = re.sub("^([-+]?)0*(.+)$", "\\1\\2", real_part)
    try:
        float(stripped_real_part)
        return stripped_real_part
    except ValueError:
        raise Exception("Uknown gcode real part: " + real_part + " in word [" + word + "]")

def to_four_digits(real):
    number = float(real)
    result = "%.4f" % number 
    return result

"""
Orders the commands into the order they actually run

The order of execution of items on a line is defined not by the position of each item on the line, but by the following list:

   1. Comment (including message)
   2. Set feed rate mode (G93, G94).
   3. Set feed rate (F).
   4. Set spindle speed (S).
   5. Select tool (T).
   6. Change tool (M6).
   7. Spindle on or off (M3, M4, M5).
   8. Coolant on or off (M7, M8, M9).
   9. Enable or disable overrides (M48, M49).
  10. Dwell (G4).
  11. Set active plane (G17, G18, G19).
  12. Set length units (G20, G21).
  13. Cutter radius compensation on or off (G40, G41, G42)
  14. Cutter length compensation on or off (G43, G49)
  15. Coordinate system selection (G54, G55, G56, G57, G58, G59, G59.1, G59.2, G59.3).
  16. Set path control mode (G61, G61.1, G64)
  17. Set distance mode (G90, G91).
  18. Set retract mode (G98, G99).
  19. Go to reference location (G28, G30) or change coordinate system data (G10) or set axis offsets (G92, G92.1, G92.2, G94).
  20. Perform motion (G0 to G3, G33, G73, G76, G80 to G89), as modified (possibly) by G53.
  21. Stop (M0, M1, M2, M30, M60).
  
  TODO: actually implement this as a precursor to splitting commands
"""
def order_commands(block_array):
    step_2_commands = frozenset(["G93", "G94"])
    step_3_commands = frozenset(["F"])
    step_4_commands = frozenset(["S"])
    step_5_commands = frozenset(["T"])
    pass
    

"""
takes a dictionary of command and real values, and creates a string for filling in from 
conversational X/Y/Z/Feed format from the values present
"""
def format_xyzf(commands):
    result = ""
    if ("X" in commands):
        result = result + "X {X:.4f} "
    if ("Y" in commands):
        result = result + "Y {Y:.4f} "
    if ("Z" in commands):
        result = result + "Z {Z:.4f} "
    if ("F" in commands):
        result = result + "Feed {F:.4f} "
    return result.strip()


"""
converts an array of gcode words representing one gcode block
to Anilam conversational commands
"""
def convert_to_conversational(block_array, original_block, line_no=-1):
    global current_arc_coords_mode
    result = ""
    # preserve whitespace
    if (len(block_array) == 0):
        return ""
    
    # Currently takes a naive approach to parsing, just look at the first word, and 
    # the subsequent arguments to determine how to translate

    # for use when we need to look up a float value by command
    commands = {}
    
    command_string = ""
    for word in block_array:
        # use a set to determine what the remaining commands are
        command_string = command_string + command_part(word)      
        # also make a map of the remaining commands to allow easy string formatting
        commands[command_part(word)] = float(real_part(word))
        
    command_set = set(command_string)
        
    #determine the command args and format it explicitly
    #error on cases not handled
    #it is expected that extraneous leading zeros have already beens stripped
    if (count_words(block_array, "G") == 1):
        # convert the case of a single G
        debug("Converting G command: " + original_block)
        real = commands["G"]
        del commands["G"]
        command_set.remove("G")
        if (real == 0):
            if (command_set.difference(set("XYZF")) == set("")):
                # if the only commands left are XYZ and F, then process it
                result = ("Rapid      " + format_xyzf(commands) + "").format(**commands)
            else:
                error("unrecognized G0 command on line: " + str(line_no))
                error("original line:")
                error(original_block)
                raise Exception("unrecognized G0 command: " + original_block)
        elif (real == 1):
            if (command_set.difference(set("XYZF")) == set("")):
            # if the only commands left are XYZ and F, then process it
                result = ("Line       " + format_xyzf(commands) + "").format(**commands)
            else:
                error("unrecognized G1 command on line: " + str(line_no))
                error("original line:")
                error(original_block)
                raise Exception("unrecognized G1 command: " + original_block)
        elif (real == 2):
            if (current_arc_coords_mode == "INC"):
            # convert the incremental coordinates to absolute to match what Anilam expects
                if ("I" in commands):
                    new_i = commands["I"] + commands["X"]
                    commands["I"] = new_i
                if ("J" in commands):
                    new_j = commands["J"] + commands["Y"]
                    commands["J"] = new_j
            if (command_set == set("XYZIJF")):
                result = "Arc Cw     X {X:.4f} Y {Y:.4f} Z {Z:.4f} XCenter {I:.4f} YCenter {J:.4f} Feed {F:.4f}".format(**commands)
            elif (command_set == set("XYZIJ")):
                result = "Arc Cw     X {X:.4f} Y {Y:.4f} Z {Z:.4f} XCenter {I:.4f} YCenter {J:.4f}".format(**commands)
            else:
                error("unrecognized G2 command on line: " + str(line_no))
                error("original line:")
                error(original_block)
                raise Exception("unrecognized G2 command: " + original_block)
        elif (real == 3):
            if (current_arc_coords_mode == "INC"):
            # convert the incremental coordinates to absolute to match what Anilam expects
                if ("I" in commands):
                    new_i = commands["I"] + commands["X"]
                    commands["I"] = new_i
                if ("J" in commands):
                    new_j = commands["J"] + commands["Y"]
                    commands["J"] = new_j
            if (commands == set("XYZIJF")):
                result = "Arc Ccw    X {X:.4f} Y {Y:.4f} Z {Z:.4f} XCenter {I:.4f} YCenter {J:.4f} Feed {F:.4f}".format(**commands)
            elif (commands == set("XYZIJ")):
                result = "Arc Ccw    X {X:.4f} Y {Y:.4f} Z {Z:.4f} XCenter {I:.4f} YCenter {J:.4f}".format(**commands)
            else:
                error("unrecognized G3 command on line: " + str(line_no))
                error("original line:")
                error(original_block)
                raise Exception("unrecognized G3 command: " + original_block)
        elif (real == 4 and command_set == set("P")):
            #dwell
            result = "Dwell {P:.4f}".format(**commands)
        elif (real == 10 and command_set == set("PRZ")):
            #tool definition
            raise Exception("tool handling not yet implemented")
        elif (real == 17 and command_set == set("")):
            result = "Plane XY"
        elif (real == 18 and command_set == set("")):
            result = "Plane ZX"
        elif (real == 19 and command_set == set("")):
            result = "Plane YZ"
        elif (real == 20 and command_set == set("")):
            result = "Unit INCH"
        elif (real == 21 and command_set == set("")):
            result = "Unit MM"
        elif (real == 80 and command_set == set("")):
            result = "DrillOff"
        elif (real == 90 and command_set == set("")):
            #Absolute distance mode
            #The default
            result = "Dim Abs"
        elif (real == 91 and command_set == set("")):
            #Incremental distance mode
            result = "Dim Inc"
        elif (real == 90.1 and command_set == set("")):
            #Arc centers I,J,K are absolute
            #Use this setting to determine how to handle IJK
            current_arc_coords_mode = "ABS"
            result = result
        elif (real == 91.1 and command_set == set("")):
            #The default
            #Arc centers I,J,K are relative to the arc's starting point
            #Use this setting to determine how to handle IJK
            current_arc_coords_mode = "INC"
            result = result
        else:
            error("unrecognized G command on line: " + str(line_no))
            error("original line:")
            error(original_block)
            raise Exception("unrecognized G command: " + original_block)
    elif (count_words(block_array, "M") == 1):
        debug("Converting M command")
        real = commands["M"]
        del commands["M"]
        command_set.remove("M")
        # convert the case of one M command
        if (real == 0 and command_set == set("")):
            #End Program 
            result = "MCode 0"
        elif (real == 2 and command_set == set("")):
            #Turn spindle clockwise
            result = "EndMain"
        elif (real == 3 and command_set == set("")):
            #Turn spindle clockwise
            result = "MCode 3"
        elif (real == 4 and command_set == set("")):
            #Turn spindle counter-clockwise
            result = "MCode 4"
        elif (real == 5 and command_set == set("")):
            #Stop spindle
            result = "MCode 5"
        elif (real == 6 and command_set == set("")):
            #Change tool
            result = "MCode 6"        
        else:
            error("unrecognized M command on line: " + str(line_no))
            error("original line:")
            error(original_block)
            raise Exception("unrecognized M command: " + str(original_block))
    elif (command_set == set("O")):
        result = "* * " + block_array[0]
    elif (command_set == set("S")):
        real = commands["S"]
        result = "RPM        {0:.4f}" .format(real)
    elif (command_set == set("T")):
        real = commands["T"]
        result = "Tool# {0:.0f}" .format(real)
    elif (command_set.difference(set("XYZF")) == set("")):
        # convert bare X/Y/Z/F lines
        result = (format_xyzf(commands) + "").format(**commands)
    else:
        error("unrecognized command on line: " + str(line_no))
        error("original line:")
        error(original_block)
        raise Exception("unrecognized command: " + str(original_block))
    return result

def usage():
    print """
    A command-line program to convert gcode files into Anilam 
    conversational format.
    Usage:
    anilampost.py --input=<input_file_name> --output=<output_file_name> [--debug]
    
    Examples:
    anilampost.py --input=TEST.G --output=TEST.M
    
    if the debug option is specified, the original gcode is written out as comments
    in-line with the converted code.
    
    """

def main():
    global log_level
    
    debug("raw arguments")
    debug(sys.argv[1:])
    if (len(sys.argv) == 1):
        usage()
        sys.exit(2)
    try:
        opts, args = getopt.getopt(sys.argv[1:], "ho:i:d", ["help", "output=", "input=","debug"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)
    output_file = None
    input_file = None
    for o, a in opts:
        if o in ("-d", "--debug"):
            log_level = 0
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-i", "--input"):
            input_file = a
        elif o in ("-o", "--output"):
            output_file = a
        else:
            assert False, "unhandled option"
    
    if (input_file == None or output_file == None):
        print("You must supply both an input file and an output file")
        sys.exit(2)
    translate_file(input_file, output_file)

# when spawned via command line, execute the main method
if __name__ == "__main__":
    main()
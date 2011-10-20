import sys

"""
The checksum is calculated as follows:
* Perform an 8-bit ADD of the hex values of each of 
the ASCII characters that are to be sent. Do not 
include the checksum byte or the carriage
return character.
* Take the sum and AND it with 7Fh . This will
limit the calculated number to the first 128 ASCII
characters.
* Now take the above result and OR it with 40h.
This will shift the characters by 40 hex characters,
effectively shifting the result to one of the
printable characters.
* Now look up the 8-bit Hex value in a standard
ASCII table to determine the character that is to
be used as the checksum.
Let's assume you wanted to send the message $1006.
The ASCII character "$" is represented by the Hex 
value 24h. The ASCII character "1" is represented by
the Hex character 31h, "0" by 30h (two times in this
example), and lastly "6" by 36h. Adding these values
gives the 8-bit result EBh. AND with 7Fh yields 6Bh.
OR with 40h yields the final result 6Bh, which is the
ASCII character lower case "k". The final transmitted
string would then be: $1006k<CR>.
"""



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
    command = command.rstrip('\n')
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
    
    
#EEPROM_VALID
print generate_command("$1A00")

dump_output(generate_command("$1A00"))

#EE_VERSION
print generate_command("$1A01")

#DRIVE_ADDRESS
print generate_command("$1B00")

#BAUD_RATE
print generate_command("$1B01")

#DRIVE_COMMAND
print generate_command("$1C00")

#DRIVE_MODE
print generate_command("$1C01")

#VDC (volts) * drive_kv
print generate_command("$1D07")

#D0A HEATSINK TEMP 0.1 C
print generate_command("$1D0A")

#D0E ELAPSED_LO 0.01 hours
print generate_command("$1D0E")

#ELAPSED_HRS hours
print generate_command("$1D0F")


print "enter a command:"
input = sys.stdin.readline()

print generate_command(input)

dump_output(generate_command(input))

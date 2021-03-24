###################################
#                                 #
#     John Moore - COMP 431       #
#   Starter server code for HW1   #
#          Version 1.2            #
###################################

# Implemented by Grant Sytniak
#
# This program parses a subset of FTP commands. It takes
# standard input from an input file that can be be generated
# by running a "MakeInput" file.
#
# This program was implemented by using helper functions to implement
# string parsing while the main read_commands function manages expected
# commands, checks for proper line endings (CRLF), and calls the helper
# functions when necessary.

import os
import sys
from socket import *

# Important ASCII character decimal representations
cr = ord('\r')  # = 13
lf = ord('\n')  # = 10
crlf_vals = [cr, lf]
space = ord(' ') # = 32
fslash = ord('/') # = 47
bslash = ord('\\') # = 92
slash_vals = [fslash, bslash]

# Global vars
#
# Some helper functions need to check global state and/or provide more
# information for the main function.
current_type = ""       # for TYPE command
host_address = ""       # current PORT command info
port_number = ""        # current PORT command info
pathname = ""           # pathname of file for RETR command
expected_commands = []  # variable list of expected commands
ftp_control = socket(AF_INET, SOCK_STREAM)

# Known server commands (case insensitive).
command_list = ["USER", "PASS", "TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]

# Valid response messages for every command
#
# Some are left empty because they are variable. Those are
# located after valid_responses is accessed in the main 
# read_commands function.
valid_responses = {
    "USER" : "331 Guest access OK, send password.\r\n",
    "PASS" : "230 Guest login OK.\r\n",
    "SYST" : "215 UNIX Type: L8.\r\n",
    "NOOP" : "200 Command OK.\r\n",
    "QUIT" : "221 Goodbye.\r\n",
    "RETR" : "150 File status okay.\r\n",
}

# Server loop
#
# This loop waits for incoming requests from clients and processes them
def server_loop():
    global ftp_control
    serverPort = int(sys.argv[1]) # 9000 + 5506 = 14506
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    while True:
        ftp_control, addr = serverSocket.accept()
        read_commands()
        ftp_control.close()
        reset_internal_state()

# Reset internal state function
def reset_internal_state():
    global current_type
    global host_address
    global port_number
    global pathname
    global expected_commands
    
    current_type = ""
    host_address = ""
    port_number = ""
    pathname = ""
    expected_commands = []

##############################################################################################
#                                                                                            # 
#     This function is intended to manage the command processing loop.                       #
#     The general idea is to loop over the input stream, identify which command              #
#     was entered, and then delegate the command-processing to the appropriate function.     #
#                                                                                            #
##############################################################################################
def read_commands():
    # Global vars
    global pathname
    global expected_commands
    # Local vars
    login_complete = False  # login status
    active = True

    # FTP service always begins with "220 COMP 431 FTP server ready.\r\n"
    send_reply("220 COMP 431 FTP server ready.\r\n")

    # Keep track of the expected commands, initially only "USER" and "QUIT" are valid commands
    expected_commands = ["USER", "QUIT"]
    while active:       # Process each FTP command
        try:
            command = ftp_control.recv(1024).decode() # 1,024 bytes
        except:
            # failed to receive command
            active = False
            continue
        if command == "":
            # failed to receive command
            active = False
            continue

        # Echo the line of input
        sys.stdout.write(command)

        # Split command into its tokens and parse relevant command
        tokens = command.split()    # Assume tokens are delimited by <SP>, <CR>, <LF>, or <CRLF>

        # Check to make sure there are tokens in the line, and assign command_name
        command_name = tokens[0].upper() if len(tokens) > 0 else "UNKNOWN"       # Commands are case-insensitive
        # Check first token in list to see if it matches any valid commands
        if command_name in command_list and not command[0].isspace():            # check known commands
            if command_name in expected_commands:                                # check expected commands
                #############################################################
                #  This is intended to delegate command processing to       #
                #  the appropriate helper function. Helper function parses  #
                #  command, performs any necessary work, and returns        #
                #  updated list of expected commands                        #
                #############################################################
                if command_name == "USER":         
                    result, expected_commands = parse_user(tokens)
                elif command_name == "PASS":         
                    result, expected_commands = parse_pass(tokens)
                elif command_name == "TYPE":        
                    result = parse_type(tokens)
                elif command_name == "SYST":         
                    result = parse_syst(tokens)
                elif command_name == "NOOP":         
                    result = parse_noop(tokens)
                elif command_name == "QUIT":
                    result = parse_quit(tokens)
                elif command_name == "PORT":         
                    result, expected_commands = parse_port(tokens)
                elif command_name == "RETR":         
                    result, expected_commands = parse_retr(tokens)
                
                ##################################################
                #  After command processing, the following code  #
                #  prints the appropriate response message       #
                ##################################################
                if result != "ok":
                    send_reply(result)
                else: # result is "ok", check for proper CRLF and no trailing space
                    if (ord(command[-1]) == lf and 
                            ord(command[-2]) == cr and 
                            (ord(command[-3]) != space or 
                                command_name == "USER" or   # string inputs can have trailing space
                                command_name == "PASS" or
                                command_name == "RETR")) :
                        # good CRLF and no trailing space, all done checking commands
                        # send responses
                        if (command_name not in ["TYPE", "PORT"]):
                            send_reply(valid_responses[command_name])
                        # some commands perform additional actions
                        if command_name == "PASS":
                            login_complete = True
                        elif command_name == "QUIT":
                            active = False
                        # RETR, TYPE, and PORT have variable messages
                        elif command_name == "RETR": # RETR can now send file
                            # try to connect
                            try:
                                ftp_data = socket(AF_INET, SOCK_STREAM)
                                ftp_data.connect((host_address, int(port_number)))
                                # send file on data socket
                                file = open(pathname, "rb")
                                ftp_data.sendall(file.read())
                                file.close()
                                ftp_data.close()
                                send_reply("250 Requested file action completed.\r\n")
                            except:
                                send_reply("425 Can not open data connection.\r\n")
                        elif command_name == "TYPE":
                            send_reply("200 Type set to " + current_type + ".\r\n")
                        elif command_name == "PORT":
                            send_reply("200 Port command successful (" + host_address + "," + port_number + ").\r\n")
                    else: # incorrect CRLF
                        send_reply("501 Syntax error in parameter.\r\n")
                        ######################################################
                        #  Update expected_commands list if incorrect CRLF   #
                        #  changes the possible commands that can come next  #     
                        ######################################################
                        if command_name == "USER":
                            expected_commands = ["USER", "QUIT"]
                        elif command_name == "PASS":
                            expected_commands = ["USER", "QUIT"]
                        elif command_name == "PORT":
                            if "RETR" in expected_commands: # RETR access stays if command is bad
                                expected_commands = ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
                            else:
                                expected_commands = ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
                        elif command_name == "RETR": # RETR access stays if command is bad
                            expected_commands = ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
            else: # Out of order command received
                if not login_complete:
                    send_reply("530 Not logged in.\r\n")
                    expected_commands = ["USER", "QUIT"]
                else: 
                    send_reply("503 Bad sequence of commands.\r\n")
        else: # No valid command was input
            send_reply("500 Syntax error, command unrecognized.\r\n")

#################################
#                               #
#       Helper functions        #
#                               #
#################################

def send_reply(message):
    sys.stdout.write(message)
    ftp_control.send(message.encode())

################################################################################
#                                                                              # 
#     Each command is parsed to check if tokens adhere to grammar              #
#     The "tokens" parameter is a list of the elements of the command          #
#     separated by whitespace. The return value indicates if the command       #
#     is valid or not, as well as the next list of valid commands.             #
#                                                                              #
################################################################################

def parse_user(tokens):
    # Check to make sure there is at least one token after "USER"
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    else:
        # Iterate through remaining tokens and check that no invalid usernames are entered
        for token in tokens[1:]:
            for char in token:
                if ord(char) > 127 or ord(char) in crlf_vals:     # Byte values > 127 along with <CRLF> are not valid for usernames
                    return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    return "ok", ["USER", "PASS", "QUIT"]      # If the function makes it here, the input adheres to the grammar for this command

def parse_pass(tokens):
    # Check to make sure there is at least one token after "PASS"
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    else:
        # Iterate through remaining tokens and check that no invalid passwords are entered
        for token in tokens[1:]:
            for char in token:
                if ord(char) > 127 or ord(char) in crlf_vals:     # Byte values > 127 along with <CRLF> are not valid for passwords
                    return "501 Syntax error in parameter.\r\n", ["USER", "QUIT"]
    return "ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]      # If the function makes it here, the input adheres to the grammar for this command

def parse_type(tokens):
    # Global vars
    global current_type
    # Check number of tokens
    if len(tokens) == 1 or len(tokens) > 2:
        return "501 Syntax error in parameter.\r\n"
    else:
        # Case insensitive
        tokens[1].upper()
        # Identify token
        if tokens[1] == "A":
            current_type = "A"
            return "ok"
        elif tokens[1] == "I":
            current_type = "I"
            return "ok"
        else:
            return "501 Syntax error in parameter.\r\n"

def parse_syst(tokens):
    # check for extra tokens
    if len(tokens) > 1:
        return "501 Syntax error in parameter.\r\n"
    else:
        return "ok"

def parse_noop(tokens):
    # check for extra tokens
    if len(tokens) > 1:
        return "501 Syntax error in parameter.\r\n"
    else:
        return "ok"

def parse_quit(tokens):
    # check for extra tokens
    if len(tokens) > 1:
        return "501 Syntax error in parameter.\r\n"
    else:
        return "ok"

def parse_port(tokens):
    # Global vars
    global host_address
    global port_number
    # Check to make sure there is at least one token after "PORT"
    if len(tokens) == 1:
        if "RETR" in expected_commands: # RETR access stays if command is bad
            return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
        else:
            return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
    else:
        # Checking paramater format
        numbers = tokens[1].split(",")
        if len(numbers) != 6:
            if "RETR" in expected_commands: # RETR access stays if command is bad
                return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
            else:
                return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
        else:
            # Iterate through numbers and check that no invalid numbers are entered
            for number in numbers:
                try: # convert to int if possible
                    intNumber = int(number)
                except:
                    if "RETR" in expected_commands: # RETR access stays if command is bad
                        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
                    else:
                        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
                if intNumber < 0 or intNumber > 255: # check int range
                    if "RETR" in expected_commands: # RETR access stays if command is bad
                        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
                    else:
                        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]
            # Parameter good, changing values, values can't be used if command has bad CRLF (RETR access revoked)    
            host_address = ".".join(numbers[:4])
            port_number = str(int(numbers[4])*256 + int(numbers[5]))
            return ("ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"])

def parse_retr(tokens):
    # Global vars
    global pathname
    # Local vars
    pathfound = False   # True when the start of the pathname has been found
    # Check to make sure there is at least one token after "RETR"
    if len(tokens) == 1:
        return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
    else:
        # verify and simplify pathname
        for token in tokens[1:]:
            for char in token:
                if ord(char) > 127 or ord(char) in crlf_vals: # checking for invalid characters
                    return "501 Syntax error in parameter.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
                elif (not pathfound): # start of pathname not found yet
                    if ((ord(char) not in slash_vals) and (ord(char) != space)): # ignoring leading slashes and spaces
                        pathfound = True
                        pathname = char # pathname begins with first char
                else: # build pathname after finding beginning
                    pathname += char
        if (not os.access(pathname, os.F_OK) or not os.access(pathname, os.R_OK)): # checking existence and access
            return "550 File not found or access denied.\r\n", ["TYPE", "SYST", "NOOP", "QUIT", "PORT", "RETR"]
        else:
            return "ok", ["TYPE", "SYST", "NOOP", "QUIT", "PORT"]


server_loop()

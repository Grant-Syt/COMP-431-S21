###################################
#      John Moore - COMP 431      #
#     FTP Client Starter Code     #
#           Version 1.0           #
###################################

# This program will ultimately be a complete FTP client according to the client specifications 
# provided in the assignment writeup. Currently, this program reads user input from stdin, 
# parses the input, and generates the appropriate FTP commands. Your task is to integrate this I/O 
# with sockets to allow actual communication with the server program. A completed client program will
# read high-level commands from stdin, convert these commands into FTP commands that get sent to the server
# over an established socket, and then parse the command replies the server sends back over the socket. 
# Additionally, file data will be read over an ftp_data connection, and subsequently written to an appropriately
# named file on the client machine.
#
# Socket implementation by Grant Sytniak

import sys
import os
from socket import *

from FTP_ReplyParser import read_reply

# Global vars
ftp_control = socket(AF_INET, SOCK_STREAM)
listeningSocket = socket(AF_INET, SOCK_STREAM)
listeningSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
listeningSocket.settimeout(6)
local_port = int(sys.argv[1])
file_count = 0
expected_commands = ["CONNECT"]

# Define dictionary of useful ASCII codes
# Use ord(char) to get decimal ascii code for char
ascii_codes = {
    "A": ord("A"), "Z": ord("Z"), 
    "a": ord("a"), "z": ord("z"), 
    "0": ord("0"), "9": ord("9"),
    "min_ascii_val": 0, "max_ascii_val": 127}

##############################################################################################
#                                                                                            # 
#     This function is intended to manage the command processing loop.                       #
#     The general idea is to loop over the input stream, identify which command              #
#     was entered, and then delegate the command-processing to the appropriate function.     #
#                                                                                            #
##############################################################################################
def read_commands():
    # Global vars
    global expected_commands
    # Initially, only the CONNECT command is valid
    expected_commands = ["CONNECT"]
    command_loop()
    ftp_control.close

def command_loop():
    # Global vars
    global local_port
    global expected_commands
    global ftp_control
    global listeningSocket
    for command in sys.stdin:
        # Echo command exactly as it was input
        sys.stdout.write(command)

        # Extract command name from input, assuming commands are case-insensitive
        command_name = command.split()[0].upper()

        if command_name in expected_commands:
            if command_name == "CONNECT":
                response, port_num, server_name = parse_connect(command)
                print(response)
                if "ERROR" not in response:
                    # valid connect command
                    # quit if already connected
                    if ("GET" in expected_commands):
                        generate_quit_output()
                    # reset state
                    expected_commands = ["CONNECT"]
                    local_port = int(sys.argv[1])
                    # try to connect
                    try:
                        ftp_control = socket(AF_INET, SOCK_STREAM)
                        ftp_control.connect((server_name, port_num))
                        success = recv_reply('FTP reply 220 accepted. Text is: COMP 431 FTP server ready.')
                        if (not success):
                            ftp_control.close()
                        else:
                            success = generate_connect_output()
                            if (not success):
                                ftp_control.close() # not sure about this *********************
                                continue
                            expected_commands = ["CONNECT", "GET", "QUIT"]
                    except:
                        print("CONNECT failed")
                        expected_commands = ["CONNECT"]
            elif command_name == "GET":
                response, file_path = parse_get(command)
                print(response)
                if "ERROR" not in response:
                    # valid get command
                    try:
                        # start listening on local_port
                        listeningSocket = socket(AF_INET, SOCK_STREAM)
                        listeningSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
                        listeningSocket.settimeout(6)
                        listeningSocket.bind(('', local_port))
                        listeningSocket.listen(1)
                        success = generate_get_output(local_port, file_path)
                        if (not success):
                            continue
                        expected_commands = ["CONNECT", "GET", "QUIT"]
                    except:
                        print("GET failed, FTP-data port not allocated.")
                        expected_commands = ["CONNECT", "GET", "QUIT"]
            elif command_name == "QUIT":
                response = parse_quit(command)
                print(response)
                if "ERROR" not in response:
                    # valid quit command
                    success = generate_quit_output()
                    if (not success):
                        continue
                    sys.exit()
        else:
            print("ERROR -- Command Unexpected/Unknown")

##############################################################
#       The following three methods are for generating       #
#       the appropriate output for each valid command.       #
##############################################################
def generate_connect_output():
    send_command("USER anonymous")
    success = recv_reply('FTP reply 331 accepted. Text is: Guest access OK, send password.')
    if (not success):
        return False
    send_command("PASS guest@")
    success = recv_reply('FTP reply 230 accepted. Text is: Guest login OK.')
    if (not success):
        return False
    send_command("SYST")
    success = recv_reply('FTP reply 215 accepted. Text is: UNIX Type: L8.')
    if (not success):
        return False
    send_command("TYPE I")
    success = recv_reply('FTP reply 200 accepted. Text is: Type set to I.')
    if (not success):
        return False
    return True

def generate_get_output(port_num, file_path):
    global file_count
    global local_port
    my_ip = gethostbyname(gethostname()).replace('.', ',')
    port_num_formatted = f"{int(int(port_num) / 256)},{int(port_num) % 256}"      # int() automatically floors its arg
    send_command(f"PORT {my_ip},{port_num_formatted}")
    success = recv_reply(f'FTP reply 200 accepted. Text is: Port command successful ({gethostbyname(gethostname())},{port_num}).')
    if (not success):
        return False
    local_port += 1
    send_command(f"RETR {file_path}")
    success = recv_reply('FTP reply 150 accepted. Text is: File status okay.')
    if (not success):
        return False
    try:
        ftp_data, addr = listeningSocket.accept()
        data = ftp_data.recv(10000000) # 1,000,000 bytes
        success = recv_reply('FTP reply 250 accepted. Text is: Requested file action completed.')
        if (not success):
            ftp_data.close()
            return False
        file_count += 1
        file = open(f"retr_files/file{file_count}", "wb")
        file.write(data)
        file.close()
        ftp_data.close()
        return True
    except:
        # timeout exception from .accept()
        # 425 Error
        return False

def generate_quit_output():
    send_command("QUIT")
    success = recv_reply('FTP reply 221 accepted. Text is: Goodbye.')
    if (not success):
        return False
    ftp_control.close()
    return True

def send_command(message):
    print(message)
    message = str(message) + '\r\n' # add CRLF
    ftp_control.send(message.encode())

def recv_reply(expected):
    reply = ftp_control.recv(1024).decode() # 1,024 bytes
    reply_message = read_reply(reply)
    error_codes = ['425','500', '501', '503', '530', '550']
    if (reply_message.split()[2] in error_codes or reply_message != expected):
        # error code or unexpected
        # end command sequence and read next input line
        print(reply_message)
        return False
    print(reply_message)
    return True


##############################################################
#         Any method below this point is for parsing         #
##############################################################

# CONNECT<SP>+<server-host><SP>+<server-port><EOL>
def parse_connect(command):
    server_host = ""

    if command[0:7] != "CONNECT" or len(command) == 7:
        return "ERROR -- request", server_host
    command = command[7:]
    
    command = parse_space(command)
    if len(command) > 1:
        command, server_host = parse_server_host(command)
    else:
        command = "ERROR -- server-host"

    if "ERROR" in command:
        return command, server_host

    command = parse_space(command)
    if len(command) > 1:
        command, server_port = parse_server_port(command)
    else:
        command = "ERROR -- server-port"

    server_port = int(server_port)
    
    if "ERROR" in command:
        return command, server_host
    elif command != '\r\n' and command != '\n':
        return "ERROR -- <CRLF>", server_host
    return f"CONNECT accepted for FTP server at host {server_host} and port {server_port}", server_port, server_host

# GET<SP>+<pathname><EOL>
def parse_get(command):
    if command[0:3] != "GET":
        return "ERROR -- request"
    command = command[3:]
    
    command = parse_space(command)
    command, pathname = parse_pathname(command)

    if "ERROR" in command:
        return command
    elif command != '\r\n' and command != '\n':
        return "ERROR -- <CRLF>"
    return f"GET accepted for {pathname}", pathname

# QUIT<EOL>
def parse_quit(command):
    if command != "QUIT\r\n" and command != "QUIT\n":
        return "ERROR -- <CRLF>"
    else:
        return "QUIT accepted, terminating FTP client"

# <server-host> ::= <domain>
def parse_server_host(command):
    command, server_host = parse_domain(command)
    if command == "ERROR":
        return "ERROR -- server-host", server_host
    else:
        return command, server_host

# <server-port> ::= character representation of a decimal integer in the range 0-65535 (09678 is not ok; 9678 is ok)
def parse_server_port(command):
    port_nums = []
    port_string = ""
    for char in command:
        if ord(char) >= ascii_codes["0"] and ord(char) <= ascii_codes["9"]:
            port_nums.append(char)
            port_string += char
        else:
            break
    if len(port_nums) < 5:
        if ord(port_nums[0]) == ascii_codes["0"] and len(port_nums) > 1:
            return "ERROR -- server-port"
        return command[len(port_nums):], port_string
    elif len(port_nums) == 5:
        if ord(port_nums[0]) == ascii_codes["0"] or  int(command[0:5]) > 65535:
            return "ERROR -- server-port"
    return command[len(port_nums):], port_string

# <pathname> ::= <string>
# <string> ::= <char> | <char><string>
# <char> ::= any one of the 128 ASCII characters
def parse_pathname(command):
    pathname = ""
    if command[0] == '\n' or command[0:2] == '\r\n':
        return "ERROR -- pathname", pathname
    else:
        while len(command) > 1:
            if len(command) == 2 and command[0:2] == '\r\n':
                return command, pathname
            elif ord(command[0]) >= ascii_codes["min_ascii_val"] and ord(command[0]) <= ascii_codes["max_ascii_val"]:
                pathname += command[0]
                command = command[1:]
            else:
                return "ERROR -- pathname", pathname
        return command, pathname

# <domain> ::= <element> | <element>"."<domain>
def parse_domain(command):
    command, server_host = parse_element(command)
    return command, server_host

# <element> ::= <a><let-dig-hyp-str>
def parse_element(command, element_string=""):
    # Keep track of all elements delimited by "." to return to calling function

    # Ensure first character is a letter
    if (ord(command[0]) >= ascii_codes["A"] and ord(command[0]) <= ascii_codes["Z"]) \
    or (ord(command[0]) >= ascii_codes["a"] and ord(command[0]) <= ascii_codes["z"]):
        element_string += command[0]
        command, let_dig_string = parse_let_dig_str(command[1:])
        element_string += let_dig_string
        if command[0] == ".":
            element_string += "."
            return parse_element(command[1:], element_string)
        elif command[0] == ' ':
            return command, element_string
        else:
            return "ERROR", element_string
    elif command[0] == ' ':
        return command, element_string
    return "ERROR", element_string

# <let-dig-hyp-str> ::= <let-dig-hyp> | <let-dig-hyp><let-dig-hyp-str>
# <a> ::= any one of the 52 alphabetic characters "A" through "Z"in upper case and "a" through "z" in lower case
# <d> ::= any one of the characters representing the ten digits 0 through 9
def parse_let_dig_str(command):
    let_dig_string = ""
    while (ord(command[0]) >= ascii_codes["A"] and ord(command[0]) <= ascii_codes["Z"]) \
    or (ord(command[0]) >= ascii_codes["a"] and ord(command[0]) <= ascii_codes["z"]) \
    or (ord(command[0]) >= ascii_codes["0"] and ord(command[0]) <= ascii_codes["9"]) \
    or (ord(command[0]) == ord('-')):
        let_dig_string += command[0]
        if len(command) > 1:
            command = command[1:]
        else:
            return command, let_dig_string
    return command, let_dig_string

# <SP>+ ::= one or more space characters
def parse_space(line):
    if line[0] != ' ':
        return "ERROR"
    while line[0] == ' ':
        line = line[1:]
    return line

read_commands()
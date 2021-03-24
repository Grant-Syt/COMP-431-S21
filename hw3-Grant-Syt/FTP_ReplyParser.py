###################################
#      John Moore - COMP 431      #
#         FTP Reply Parser        #
#           Version 1.0           #
###################################

# This program is intended to provide the base framework for parsing FTP_Server replies 
# to the commands that get sent by FTP_Client.py. Currently, these replies are simulated by 
# reading lines from stdin. Your task is to integrate this code into FTP_Client.py and 
# validate the replies received from the socket connection instead of stdin. 

import sys

# Define dictionary of useful ASCII codes
# Use ord(char) to get decimal ascii code for char
ascii_codes = {
    "A": ord("A"), "Z": ord("Z"), 
    "a": ord("a"), "z": ord("z"), 
    "0": ord("0"), "9": ord("9"),
    "min_ascii_val": 0, "max_ascii_val": 127}

# Function that reads and parses "server reply lines" from stdin
# **** Not used anymore ****
def read_replies():
    for reply in sys.stdin:
        # Echo the line of input (i.e., print the line of input unchanged to standard output).
        sys.stdout.write(reply)

        # Check to see if reply is a valid FTP reply
        resp = parse_reply(reply)
        print(resp)

# Function that reads and parses a real server reply line
# **** called from FTP_Client ****
def read_reply(reply):
    return parse_reply(reply)

##############################################################
#         Any method below this point is for parsing         #
##############################################################
# <reply-code><SP><reply-text><CRLF> 
def parse_reply(reply):
    # <reply-code>
    reply, reply_code = parse_reply_code(reply)
    if "ERROR" in reply:
        return reply
    
    # <SP>
    reply = parse_space(reply)
    if "ERROR" in reply:
        return "ERROR -- reply-code"
    
    # <reply-text>
    reply, reply_text = parse_reply_text(reply)
    if "ERROR" in reply:
        return reply
    
    # <CRLF>
    if reply != '\r\n' and reply != '\n':
        return "ERROR -- <CRLF>"
    return f"FTP reply {reply_code} accepted. Text is: {reply_text}"

# <reply-code> ::= <reply-number>  
def parse_reply_code(reply):
    reply, reply_code = parse_reply_number(reply)
    if "ERROR" in reply:
        return "ERROR -- reply-code", reply_code
    return reply, reply_code

# <reply-number> ::= character representation of a decimal integer in the range 100-599
def parse_reply_number(reply):
    reply_number = 0
    if len(reply) < 3:
        return "ERROR", reply_number
    try:
        reply_number = int(reply[0:3])
    except ValueError:
        return "ERROR", reply_number
    reply_number = reply[0:3]
    if int(reply_number) < 100 or int(reply_number) > 599:
        return "ERROR", reply_number
    return reply[3:], reply_number

# <reply-text> ::= <string>
# <string> ::= <char> | <char><string>
# <char> ::= any one of the 128 ASCII characters
def parse_reply_text(reply):
    reply_text = ""
    if reply[0] == '\n' or reply[0:2] == '\r\n':
        return "ERROR -- reply_text", reply_text
    else:
        while len(reply) > 1:
            if len(reply) == 2 and reply[0:2] == '\r\n':
                return reply, reply_text
            elif ord(reply[0]) >= ascii_codes["min_ascii_val"] and ord(reply[0]) <= ascii_codes["max_ascii_val"]:
                reply_text += reply[0]
                reply = reply[1:]
            else:
                return "ERROR -- reply_text", reply_text
        return reply, reply_text

# <SP>+ ::= one or more space characters
def parse_space(reply):
    if reply[0] != ' ':
        return "ERROR"
    while reply[0] == ' ':
        reply = reply[1:]
    return reply

# read_replies()
import sys

sys.stdout.write("220 COMP 431 FTP server ready.\r\n")

sys.stdout.write("user                  name\r\n")
sys.stdout.write("331 Guest access OK, send password.\r\n")
sys.stdout.write("pass                  word\r\n")
sys.stdout.write("230 Guest login OK.\r\n")

sys.stdout.write("retr           //\\\\ not_readable.txt\r\n") # bad sequence
sys.stdout.write("503 Bad sequence of commands.\r\n")
sys.stdout.write("port                  1,2,3,4,5,6\r\n")
sys.stdout.write("200 Port command successful (1.2.3.4,1286).\r\n")


sys.stdout.write("retr           //\\\\ does_not_exist.txt\r\n") # DNE
sys.stdout.write("550 File not found or access denied.\r\n")
sys.stdout.write("retr           //\\\\ not_readable.txt\r\n") # not readable
sys.stdout.write("550 File not found or access denied.\r\n")
sys.stdout.write("retr           //\\\\ Æyeet.txt\r\n") # bad char
sys.stdout.write("501 Syntax error in parameter.\r\n")
sys.stdout.write("retr           //\\\\ yeet.txt\r\n") # valid
sys.stdout.write("150 File status okay.\r\n")
sys.stdout.write("250 Requested file action completed.\r\n")

sys.stdout.write("port                  1,2,3,4,5,6\r\n")
sys.stdout.write("200 Port command successful (1.2.3.4,1286).\r\n")
sys.stdout.write("retr           //\\\\ retr_test/test/yeet.txt\r\n") # valid
sys.stdout.write("150 File status okay.\r\n")
sys.stdout.write("250 Requested file action completed.\r\n")

sys.stdout.write("quit\r\n")
sys.stdout.write("200 Command OK.\r\n")
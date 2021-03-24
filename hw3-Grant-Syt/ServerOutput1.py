import sys
client_ip = "152.19.160.146"
client_port = 14507
client_ip_commas = "152,19,160,146"
client_deconstructed_port = "56,171"

sys.stdout.write("220 COMP 431 FTP server ready.\r\n")

sys.stdout.write("USER anonymous\r\n")
sys.stdout.write("331 Guest access OK, send password.\r\n")
sys.stdout.write("PASS guest@\r\n")
sys.stdout.write("230 Guest login OK.\r\n")
sys.stdout.write("SYST\r\n")
sys.stdout.write("215 UNIX Type: L8.\r\n")
sys.stdout.write("TYPE I\r\n")
sys.stdout.write("200 Type set to I.\r\n")

sys.stdout.write("QUIT\r\n")
sys.stdout.write("221 Goodbye.\r\n")

sys.stdout.write("220 COMP 431 FTP server ready.\r\n")

sys.stdout.write("USER anonymous\r\n")
sys.stdout.write("331 Guest access OK, send password.\r\n")
sys.stdout.write("PASS guest@\r\n")
sys.stdout.write("230 Guest login OK.\r\n")
sys.stdout.write("SYST\r\n")
sys.stdout.write("215 UNIX Type: L8.\r\n")
sys.stdout.write("TYPE I\r\n")
sys.stdout.write("200 Type set to I.\r\n")

sys.stdout.write(f"PORT {client_ip_commas},{client_deconstructed_port}\r\n")
sys.stdout.write(f"200 Port command successful ({client_ip},{client_port}).\r\n")
sys.stdout.write("RETR README.md\r\n")
sys.stdout.write("150 File status okay.\r\n")
sys.stdout.write("250 Requested file action completed.\r\n")

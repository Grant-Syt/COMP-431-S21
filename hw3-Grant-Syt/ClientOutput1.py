server = "comp431-1sp21b.cs.unc.edu"
server_port = 14506
client_ip = "152.19.160.146"
client_port = 14507
client_ip_commas = "152,19,160,146"
client_deconstructed_port = "56,171"

print(f"CONNECT {server} {server_port}")
print(f"CONNECT accepted for FTP server at host {server} and port {server_port}")
print("FTP reply 220 accepted. Text is: COMP 431 FTP server ready.")
print("USER anonymous")
print("FTP reply 331 accepted. Text is: Guest access OK, send password.")
print("PASS guest@")
print("FTP reply 230 accepted. Text is: Guest login OK.")
print("SYST")
print("FTP reply 215 accepted. Text is: UNIX Type: L8.")
print("TYPE I")
print("FTP reply 200 accepted. Text is: Type set to I.")

print(f"CONNECT {server} {server_port}")
print(f"CONNECT accepted for FTP server at host {server} and port {server_port}")
print("QUIT")
print("FTP reply 221 accepted. Text is: Goodbye.")
print("FTP reply 220 accepted. Text is: COMP 431 FTP server ready.")
print("USER anonymous")
print("FTP reply 331 accepted. Text is: Guest access OK, send password.")
print("PASS guest@")
print("FTP reply 230 accepted. Text is: Guest login OK.")
print("SYST")
print("FTP reply 215 accepted. Text is: UNIX Type: L8.")
print("TYPE I")
print("FTP reply 200 accepted. Text is: Type set to I.")

print("GET README.md")
print("GET accepted for README.md")
print(f"PORT {client_ip_commas},{client_deconstructed_port}")
print(f"FTP reply 200 accepted. Text is: Port command successful ({client_ip},{client_port}).")
print("RETR README.md")
print("FTP reply 150 accepted. Text is: File status okay.")
print("FTP reply 250 accepted. Text is: Requested file action completed.")

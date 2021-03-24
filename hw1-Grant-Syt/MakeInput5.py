import sys

# mainly testing RETR

# sys.stdout.write("user                  name\r\n")
# sys.stdout.write("pass                  word\r\n")
# sys.stdout.write("retr           //\\\\ not_readable.txt\r\n") # unexpected
# sys.stdout.write("port                  1,2,3,4,5,6\r\n")
# sys.stdout.write("retr           //\\\\ does_not_exist.txt\r\n") # DNE
# sys.stdout.write("retr           //\\\\ not_readable.txt\r\n") # not readable
# sys.stdout.write("retr           //\\\\ Æyeet.txt\r\n") # bad char
# sys.stdout.write("retr           //\\\\ yeet.txt\r\n") # valid
# sys.stdout.write("port                  1,2,3,4,5,6\r\n")
# sys.stdout.write("retr           //\\\\ retr_test/test/yeet.txt\r\n") # valid
# sys.stdout.write("quit\r\n")

# sys.stdout.write("USER j m o o r e     \r\n")
# sys.stdout.write("PASS   w   o   r   d\r\n")
# sys.stdout.write("TYPE     A\r\n")
# sys.stdout.write("TYPE     I\r\n")

sys.stdout.write("USER anonymous\r\n")
sys.stdout.write("PASS word\r\n")
sys.stdout.write("PORT a,b,c,d,e,f\r\n")
sys.stdout.write("PORT 1,a,2,b,3,c\r\n")
sys.stdout.write("PORT 1, 2, 3, 4, 5, 6\r\n")
sys.stdout.write("PORT 10,1,1,0,12,255\r\n")
import socket, sys

s = socket.socket()
s.connect(("localhost", 9000))
s.send(f"{sys.argv[1]} {sys.argv[2]}".encode())
wid, hasil = s.recv(1024).decode().split(" ", 1)
print(f"Dibalas worker {wid}: {hasil}")
s.close()

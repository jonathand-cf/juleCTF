#!/usr/bin/env python3
import subprocess

# Read the checking code from file offset 0x65
result = subprocess.run(['dd', 'if=tricky_decomp', 'bs=1', 'skip=101', 'count=512'], 
                       capture_output=True)
checking_code = bytearray(result.stdout)

# Get the key from file offset 0x1363
result2 = subprocess.run(['dd', 'if=tricky_decomp', 'bs=1', 'skip=4963', 'count=27'],
                        capture_output=True)
xor_key = result2.stdout

print(f"Key ({len(xor_key)} bytes): {xor_key.hex()}")

# Apply XOR transformation with stride 0x11 (17)
pos = 0
for i in range(27):
    if pos < len(checking_code):
        orig = checking_code[pos]
        checking_code[pos] ^= xor_key[i]
        print(f"Pos {pos:3d}: 0x{orig:02x} XOR 0x{xor_key[i]:02x} = 0x{checking_code[pos]:02x}")
    pos += 17

print(f"\nFirst 100 decrypted bytes:\n{checking_code[:100].hex()}")

# Save for disassembly
with open('decrypted_code.bin', 'wb') as f:
    f.write(checking_code)
print("\nSaved to decrypted_code.bin")

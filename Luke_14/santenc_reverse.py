from email.mime import base
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

dr = 'santaware'
enc_files = sorted([f for f in os.listdir(dr) if f.endswith('.enc')])

headers = {}
for fname in enc_files:
    with open(os.path.join(dr, fname), 'rb') as fr:
        b = fr.read(1)
        if not b:
            raise SystemExit(f"{fname} empty")
        headers[fname[:-4]] = b[0]

ordered_bases = sorted([b for b in headers.keys() if b.endswith('.txt') or b.endswith('.png')])
print("ordered_bases:", ordered_bases)
if len(ordered_bases) < 16:
    print("Have", len(ordered_bases), "leaked bytes — will brute-force the remaining bytes.")

key_bytes = bytearray(16)
for i, base in enumerate(ordered_bases):
    key_bytes[i] = headers[base]

png_base = None
for b in ordered_bases:
    if b.endswith('.png'):
        png_base = b
        break
if not png_base:
    png_base = ordered_bases[0]
print("validating with:", png_base)

with open(os.path.join(dr, png_base + '.enc'), 'rb') as fr:
    ct = fr.read()[1:]

png_sig = b'\x89PNG\r\n\x1a\n'
found = False
for b14 in range(256):
    key_bytes[14] = b14
    for b15 in range(256):
        key_bytes[15] = b15
        key = bytes(key_bytes)
        cipher = AES.new(key, AES.MODE_ECB)
        pt = cipher.decrypt(ct)
        if pt.startswith(png_sig):
            print("Found key bytes:", b14, b15)
            full_key = key
            found = True
            break
    if found:
        break

if not found:
    print("No key found (unexpected).")
    raise SystemExit(1)

cipher = AES.new(full_key, AES.MODE_ECB)
for fname in enc_files:
    path = os.path.join(dr, fname)
    with open(path, 'rb') as fr:
        data = fr.read()
    ciphertext = data[1:]
    plaintext = cipher.decrypt(ciphertext)
    try:
        plaintext = unpad(plaintext, 16)
    except Exception:
        pass
    out_path = os.path.join('presents', fname[:-4])
    with open(out_path, 'wb') as fw:
        fw.write(plaintext)

print("Decryption done. Key (hex):", full_key.hex())

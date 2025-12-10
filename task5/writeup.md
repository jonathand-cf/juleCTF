# Tricky Decomp - CTF Writeup

**Challenge Name:** Tricky Decomp  
**Author:** andreas  
**Description:** My decompiler isn't super helpful with this program...  

## Overview

This challenge provides a 32-bit x86 ELF binary that acts as a flag checker. The twist? It uses self-modifying code to decrypt its own checking logic at runtime, making static analysis misleading.

## Initial Analysis

Running `file` on the binary:

```bash
$ file tricky_decomp
tricky_decomp: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), statically linked, stripped
```

Basic strings extraction reveals:

```
Welcome to my flag checker!
Please enter the flag to verify: 
Correct!
Incorrect!
```

## The Deception

Initial disassembly shows character-by-character checks that appear to validate:

```
JUL{it_surely_cant_be_this_easy}
```

However, testing this flag results in "Incorrect!" - the checking code is encrypted!

## Understanding the Self-Modifying Code

### The Transformation Function

At address `0x804934c` (data section), there's a transformation function that gets called BEFORE reading user input:

```asm
mov ebx, ecx       ; ebx = 0x80492f8 (data section start)
add ebx, edx       ; ebx += 0x3e
add ebx, 0x2d      ; ebx += 0x2d = 0x8049363 (XOR key location)
mov ecx, 0x1b      ; counter = 27 iterations
loop:
  mov al, [ebx]    ; al = key[i]
  xor [esi], al    ; XOR code at esi
  add esi, 0x11    ; esi += 17 (stride)
  inc ebx          ; next key byte
  loop
ret
```

### Execution Flow

1. **Print prompt** - displays "Welcome to my flag checker!"
2. **Call transformation** - XORs checking code with hardcoded key
3. **Read input** - reads up to 100 bytes (expects 33 including newline)
4. **Execute decrypted checks** - validates input character by character
5. **Print result** - "Correct!" or "Incorrect!"

## Solution

### Step 1: Extract the XOR Key

The 27-byte XOR key is located at file offset `0x1363`:

```
0e 6e 03 2b 6f 2a 0e 26 55 44 5a 58 3d 17 06 17 37 1c 0b 53 18 51 44 11 00 6f 04
```

### Step 2: Locate Encrypted Expected Values

The checking code starts at file offset `0x65`. The expected character values in the comparison instructions are at positions `0x6a, 0x7b, 0x8c...` (stride of 17).

### Step 3: Decrypt the Expected Values

Apply XOR with stride 17 to extract the 27 decrypted expected characters:

```python
# Read checking code
with open('tricky_decomp', 'rb') as f:
    f.seek(0x6a)
    code = bytearray(f.read(600))

# Read XOR key
with open('tricky_decomp', 'rb') as f:
    f.seek(0x1363)
    xor_key = f.read(27)

# Apply XOR transformation
pos = 0
for i in range(27):
    if pos < len(code):
        code[pos] ^= xor_key[i]
    pos += 17

# Extract decrypted characters
decrypted_chars = []
for i in range(27):
    decrypted_chars.append(chr(code[i * 17]))
```

### Step 4: Map to Input Positions

The checks validate input positions in a scrambled order:

```python
check_offsets = [
    0x0b, 0x12, 0x14, 0x11, 0x06, 0x08, 0x04, 0x0c, 0x0a, 0x05,
    0x18, 0x1e, 0x13, 0x07, 0x1d, 0x19, 0x0d, 0x1b, 0x10, 0x0e,
    0x09, 0x1c, 0x16, 0x0f, 0x1a, 0x15, 0x17
]
```

Build the flag by placing each decrypted character at its corresponding offset:

```python
flag_bytes = bytearray(32)
flag_bytes[0:4] = b'JUL{'
flag_bytes[31] = ord('}')

for i, offset in enumerate(check_offsets):
    flag_bytes[offset] = ord(decrypted_chars[i])

flag = flag_bytes.decode('latin-1')
```

## Flag

```
JUL{g00d_j0b_h0pe_1_f00l3d_y0u!}
```

## Key Takeaways

- **Self-modifying code** can hide the true validation logic from static analysis
- The checking code is encrypted in the binary and only decrypted at runtime
- Decompilers show the encrypted checks, not the actual expected values
- Understanding the transformation function is crucial to extracting the real flag
- The check order is scrambled, requiring careful mapping of positions

## Tools Used

- `objdump` - Disassembly
- `xxd` - Hex dump analysis
- Python - XOR decryption and flag extraction
- `readelf` - Section header analysis

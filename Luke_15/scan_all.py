
import sys

def scan_all(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    base_addr = 0x400000 # Standard mapping
    
    # 5f = pop rdi
    # 5e = pop rsi
    # 5a = pop rdx
    # 59 = pop rcx
    # 58 = pop rax
    # 5b = pop rbx
    # 5d = pop rbp
    # 41 5f = pop r15
    # 41 5e = pop r14
    # 41 5d = pop r13
    # 41 5c = pop r12
    
    opcodes = {
        b'\x5f': 'pop rdi',
        b'\x5e': 'pop rsi',
        b'\x5a': 'pop rdx',
        b'\x59': 'pop rcx',
        b'\x58': 'pop rax',
        b'\x5b': 'pop rbx',
        b'\x5d': 'pop rbp',
        b'\x41\x5f': 'pop r15',
        b'\x41\x5e': 'pop r14',
    }

    print("Scanning for all pops...")
    for byte_seq, name in opcodes.items():
        pos = -1
        while True:
            pos = data.find(byte_seq, pos + 1)
            if pos == -1:
                break
            
            # Check what follows
            if pos + len(byte_seq) < len(data):
                next_byte = data[pos + len(byte_seq)]
                if next_byte == 0xc3:
                    print(f"MATCH: {name}; ret at offset {pos:x} -> VA {base_addr + pos:x}")
                elif next_byte == 0xc2:
                     print(f"MATCH: {name}; ret N at offset {pos:x} -> VA {base_addr + pos:x}")
                else:
                    # just print it if it looks like code?
                    if 0x1350 <= pos <= 0x1e3c: # Text section roughly
                         print(f"Possible {name} at offset {pos:x} -> VA {base_addr + pos:x} followed by {hex(next_byte)}")

if __name__ == "__main__":
    scan_all("main2")

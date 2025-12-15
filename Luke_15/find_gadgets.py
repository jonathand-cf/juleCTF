
import sys

def find_gadgets(filename):
    with open(filename, 'rb') as f:
        data = f.read()

    # Base address assumption based on typical ELF
    base_addr = 0x400000

    print("Searching for gadgets...")

    pops = {
        b'\x5f': 'pop rdi',
        b'\x5e': 'pop rsi',
        b'\x5a': 'pop rdx',
        b'\x59': 'pop rcx',
        b'\x58': 'pop rax',
        b'\x5b': 'pop rbx',
        b'\x5d': 'pop rbp',
        b'\x41\x5f': 'pop r15',
        b'\x41\x5e': 'pop r14',
        b'\x41\x5d': 'pop r13',
        b'\x41\x5c': 'pop r12',
    }
    
    def check(seq, name):
         pos = -1
         while True:
            pos = data.find(seq + b'\xc3', pos + 1)
            if pos == -1:
                break
            if 0x1000 <= pos <= 0x3000:
                print(f"Found {name}; ret at offset {pos:x} -> VA {base_addr + pos:x}")

    for seq, name in pops.items():
        check(seq, name)

    # Search for CSU init pop sequence
    csu_seq = b'\x5b\x5d\x41\x5c\x41\x5d\x41\x5e\x41\x5f\xc3'
    pos = data.find(csu_seq)
    if pos != -1:
        print(f"Found __libc_csu_init gadget chain end at offset {pos:x} -> VA {base_addr + pos:x}")

if __name__ == "__main__":
    find_gadgets("main2")

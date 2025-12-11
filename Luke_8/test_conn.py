from pwn import *
import sys

try:
    p = remote('snow-factory.julec.tf', 1337, ssl=True)
    print("Connected")
    data = p.recv(timeout=5)
    print(f"Received: {data}")
    p.sendline(b'%p')
    response = p.recv(timeout=5)
    print(f"Response: {response}")
    p.close()
except Exception as e:
    print(f"Error: {e}")

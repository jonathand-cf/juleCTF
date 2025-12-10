#!/usr/bin/env python3
import socket, ssl

sock = socket.socket()
conn = ssl.create_default_context().wrap_socket(sock, server_hostname='rsa-w.julec.tf')
conn.connect(('rsa-w.julec.tf', 1337))

data = b""
while b"MEG:" not in data:
    data += conn.recv(4096)

conn.sendall(("X" * 350 + "\n").encode())

result = b""
while chunk := conn.recv(4096):
    result += chunk
conn.close()

output = result.decode('utf-8', errors='ignore')
N = int([l for l in output.split('\n') if 'N=' in l][0].split('N=')[1])
w = int([l for l in output.split('\n') if 'w=' in l][0].split('w=')[1])

message_bytes = (w * N).to_bytes((w * N).bit_length() // 8 + 1, 'big')
print(message_bytes.decode())
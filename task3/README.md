# RSA...W? - Writeup

## Challenge Description

**Challenge:** RSA...W?  
**Category:** Cryptography  
**Connection:** `ncat --ssl rsa-w.julec.tf 1337`

> JULENISSEN er på oppdrag i julen og må kunne levere gaver til alle snille barn. Selv om gaven er stor eller liten, skal den komme trygt frem til barna.
>
> Med en liten modifikasjon på krypteringsalgoritmen kan JULENISSEN endelig sende selv de aller største gavene! Har du vært snill og kan få en gave?

(Translation: Santa is on a mission and must deliver gifts to all good children. Whether the gift is large or small, it should arrive safely. With a small modification to the encryption algorithm, Santa can finally send even the LARGEST gifts! Have you been good and can you get a gift?)

## Initial Reconnaissance

Connecting to the server, we're greeted by Santa asking why we want the flag. After we provide input, the server responds with RSA parameters:

```txt
JULENISSEN: Hvorfor vil du ha flagget?

MEG: Jeg vil ha flagget (SENSURERT) fordi 
[our input]

---
N=<large number>
e=65537
w=0
c=<ciphertext>
---
```

We're also provided with the source code (`rsa-w.py`), which shows the modified RSA implementation:

```python
message = f"Jeg vil ha flagget ({FLAG}) fordi "
message += answer.strip()

m = bytes_to_long(message.encode("utf-8"))

p = getPrime(1024)
q = getPrime(1024)
N = p * q
e = 2 ** 16 + 1

w = m // N      # Integer division - the quotient
m = m % N       # Modulo - the remainder
c = pow(m, e, N)
```

## The Vulnerability

The key modification is this:

```python
w = m // N
m = m % N
```

In standard RSA, if your message is larger than N, you'd split it into multiple blocks. Here, they're using a different approach:

- `w` stores how many times N "fits into" the message (the quotient)
- `m` becomes just the remainder after dividing by N
- Only the remainder is encrypted and given as `c`
- **But we also get `w` in plaintext!**

The challenge description hints at this: "even the LARGEST gifts" - this is about handling messages larger than N!

## The Insight

When we send a short input, the total message is smaller than N (256 bytes), so `w = 0`. The entire message fits in one RSA "block" and gets encrypted normally.

But what if we send a **very long input**?

If the total message is larger than N:

```python
message = w * N + remainder
```

We know `w`, we know `N`, so we can calculate `w * N`. This gives us the high-order bytes of the message **in plaintext**!

The message structure is:

```python
"Jeg vil ha flagget (" + FLAG + ") fordi " + [our input]
```

If our input is long enough (350+ bytes), the total message becomes ~416 bytes. Since N is only ~256 bytes:

- The first ~160 bytes go into `w * N` (unencrypted)
- The last ~256 bytes are encrypted in `c`

The prefix (including the FLAG) is only ~66 bytes, so it's entirely contained in the unencrypted `w * N` part!

## Solution

```python
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
start = message_bytes.index(b"JUL{")
end = message_bytes.index(b"}", start) + 1
print(message_bytes[start:end].decode())
```

Running this:

```bash
$ python3 solve.py
JUL{st0re_g4ver_0g_st0re_s1kkerhetshull}
```

## Flag

**`JUL{st0re_g4ver_0g_st0re_s1kkerhetshull}`**

(Translation: "large gifts and large security holes")

## What we can learn

Sometimes the simplest solution is the right one. The challenge description literally told us it was about "the LARGEST gifts", sending a large input was the intended path, not complex lattice attacks.

The vulnerability: when handling messages larger than the modulus, leaking `w = m // N` reveals the high-order bits of the plaintext in a directly exploitable way.

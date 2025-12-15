# santaware — writeup

- **Challenge name:** santaware
- **Author:** r3dsh3rl0ck

**Description:**
Mr Elfious has run a strange programme which is supposed to sort the current present list. However, he cannot open the current letters... Can you help him resolve this issue before Santa returns from his lunch break?

**Handout:** `santaware/` (contains `.enc` files and the encryptor `santenc.py`)

## Summary

- `santenc.py` uses AES-128 in ECB mode with a single random 16-byte key for all files.
- For each file it writes one byte of the key as a 1-byte header, then the AES-ECB ciphertext: `fw.write(bytes([key[i]]) + cipher.encrypt(padded))`.
- Because the script leaks one key byte per encrypted file (in a deterministic sorted order), an attacker can recover known positions of the key by reading those headers.
- If all 16 key bytes are leaked across files, the key is trivially reconstructed. If some bytes are missing, the remaining bytes can be brute-forced (feasible for small counts, e.g., 2 missing bytes → 65,536 trials).

## Exploit approach

1. Collect the first byte of each `.enc` file (the leaked key byte). The encryption script uses the sorted list of plaintext filenames to decide which key byte to write for each file — match that ordering when reconstructing the key.
2. Reconstruct the known key positions from the leaked header bytes. For any unknown positions, brute-force the remaining possible byte values.
3. Validate candidate keys by decrypting a file with a known signature (e.g., `little-hax0r.png` has a PNG header `\x89PNG\r\n\x1a\n`) or by checking plaintext legibility for text files.
4. Once the full key is found, decrypt all ciphertexts (strip the header byte, decrypt with AES-ECB, then unpad) and write the outputs.

## Files / scripts included

- `santaware/santenc.py` — the encryptor (leaks 1 key byte per file).
- `santenc_reverse.py` — decryption + brute-force helper that:
  - reads leaked header bytes from `.enc` files,
  - reconstructs known key bytes,
  - brute-forces missing bytes (using PNG signature to validate),
  - writes decrypted outputs into the `presents/` directory,
  - prints the recovered AES key in hex.

## Exploit

Make sure you use Python 3.11 (or under) and have `pycryptodome` and `pycrypto`.

**Ran the recovery**:

```bash
python3.11 santenc_reverse.py
```

The script prints the progress and the recovered key (hex) on success, and write decrypted files into the `presents/` directory.

## Notes

- ECB mode is used here; reusing the same AES key and leaking bytes makes the scheme insecure.
- Brute-forcing is practical when only a small number of key bytes are missing. If many bytes are missing, the search becomes infeasible.

## Recovered flag

- **Flag:** `JUL{santaware_down_time_for_gifts}`
- **Found in:** `presents/little-hax0r.png`
- **Recovered AES key (hex):** dccf295664a27a378adc0217698a5dfe

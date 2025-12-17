# santa hunter

**Author**: wuurrd

**Description**:
>Unfortunately Santa is hiding from you. Can you find him?
>Each connection is handled by a new eager elf to handle your search, complete with a tiny, magical pocket watch—a Stack Canary—to detect any tampering with its stack, and like all good elfs from the north pole their watches are set to the same time

**Handout**: [main2](main2)

# Writeup

## Challenge Summary

The service asks for a length, then reads that many bytes into a 40-byte stack
buffer. A stack canary is present, but it is static across connections. The goal
is to reach the sleigh location after the flag is loaded into the global
`location` buffer by `load_flag_to_location`.

## Vulnerability

In `greet_user`, the program does:

1) Reads a user-supplied length as a string.
2) Uses that length in `recv` into a 40-byte stack buffer.

This allows a classic stack overflow if we also supply the correct canary.

## Canary

Brute forcing is possible because:

- A wrong byte triggers stack smashing and the connection dies.
- A correct prefix survives and shows the next prompt.
- The canary is static across forked connections.

Recovered canary:

```txt
00b192664259614e
```

## Exploit Strategy

We return from `greet_user` into `load_flag_to_location` (0x401b72) so it runs:

- `popen("cat flag.txt", "r")`
- `fgets(location, 0x80, ...)`
- `play_game(fd)`

`play_game` uses the same socket fd already in `rdi`, so it is safe to reuse.

Important detail: stack alignment. Entering `load_flag_to_location` from a
non-standard call site can leave the stack misaligned, which can break libc
calls. Adding a single `ret` gadget before the function aligns the stack and
stabilizes `popen`.

Payload layout:

- 40 bytes padding
- 8-byte canary
- 8 bytes junk (saved rbp)
- 8 bytes `ret` gadget (0x40101a)
- 8 bytes `load_flag_to_location` (0x401b72)

After the call, we navigate:

```bash
3
1
```

to reach the sleigh path, which prints `location`.

## Final Flag

```txt
JUL{f0rking_s3rv3rs_m34n5_m0re_ch4nc3s_t0_brut3}
```

## Reproduction

```bash
python3 exploit.py --bruteforce
python3 exploit.py --canary 00b192664259614e
```

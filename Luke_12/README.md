# Writeup: Julespråk Fengsel

**desciption**:
>Er det et julemirakel? Publikumsfavoritten fra i fjor, julespråk, gjør comeback! Nå som fengsel!

>Klarer du å finne passende julespråk?

>For de som ikke deltok i fjor, har jeg også lagt med fjorårets oppgave fordi den kan gi viktig informasjon om språket, men denne er altså IKKE en del av årets oppgave.

**made by**: olefredrik

## Challenge Description

**Objective:** The challenge provides a "prison" service running on `julesprak-fengsel.julec.tf 1337`. It asks for a "Julespråk program". We are given the source code of the service in `app/server.js` (which is actually a Python script disguised by a custom interpreter `app/julesprak`) and the interpreter binary itself.

The goal is to provide input that bypasses a strict filter (disallowing almost all standard ASCII characters) and evaluates to the string `"Julespråk er favorittspråket mitt!"`. If successful, it prints the flag.

## Analysis

### The Interpreter

The `app/julesprak` binary is a Python 3.x interpreter with a custom initialization that aliases standard Python syntax to emojis and Norwegian words.
Running `strings` or just testing in a REPL reveals:

- **Keywords:** `hvis` (if), `ellers` (else), `fra` (from), `importer` (import), `som` (as) etc.
- **Builtins:** `print`, `eval`, `input`, etc. are available.
- **Special Emojis:**
  - `🎁` (Function)
  - `🎿` (range)
  - `🏂` (True / 1)
  - `🥛` (Function)
  - `🥶` (False / 0)
  - `🦌` (bytes type)
  - `🧣` (Function)
  - `🎈` / `🎇` -> `(` / `)`
  - `🎉` / `🎊` -> `[` / `]`
  - `🎺` -> `,`
  - `📜` -> `decode` method on bytes objects.

### The Sandbox (`server.js`)

The server script performs the following check:

```python
def sjekk_input(data):
    forbudte_tegn = """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,"'()[]=🧣"""
    hvis len(data) > 5000:
        returner 0
    for tegn inni normaliser("NFKC", data):
        hvis tegn inni forbudte_tegn:
            returner 0
    returner 1
```

It forbids all alphanumeric characters, standard parentheses, quotes, and some punctuation. However, it allows most emojis and bitwise operators like `|`, `&`, `^`, `<<`, `>>`, `+`, `-`, `*` (if not in forbidden list - `*` is not forbidden, `+` is not forbidden).

### Solution Strategy

Since we cannot simply write string literals (no quotes allowed) or numbers (no digits allowed), we must construct them using available primitives.

1. **Numbers**: We can generate any integer using `🏂` (1) and `🥶` (0) with bitwise shifting (`<<`) and addition/OR.
    - Example: `5` = `101` binary = `(1<<2) | 1`.
2. **Strings**: We cannot create string literals directly. However, we have access to the `bytes` type via `🦌`.
    - We can construct a list of integers representing UTF-8 bytes: `🎉num1🎺num2...🎊`.
    - We can create a bytes object: `🦌🎈list_of_ints🎇`.
    - we can decode it to a string using the `📜` method (which stands for `decode`): `bytes_obj.📜🎈🎇`.

    Effectively: `bytes([74, 117, ...]).decode()` -> `"Ju..."`

3. **Payload**: We need the expression to evaluate to `"Julespråk er favorittspråket mitt!"`.

## Solver Script

We wrote a script to automate the generation of this Julespråk payload.

```python
import sys

def to_julesprak(n):
    if n == 0:
        return "🥶"
    if n == 1:
        return "🏂"
    
    shift = n.bit_length() - 1
    
    base = f"🏂<<🎈{to_julesprak(shift)}🎇" if shift > 0 else "🏂"
    
    remainder = n - (1 << shift)
    if remainder == 0:
        return base
    else:
        return f"🎈{base}|{to_julesprak(remainder)}🎇"

BYTES = "🦌"
LPAREN = "🎈"
RPAREN = "🎇"
LBRACKET = "🎉"
RBRACKET = "🎊"
COMMA = "🎺"
DECODE = "📜"

target = "Julespråk er favorittspråket mitt!"
encoded_bytes = target.encode('utf-8')

byte_expressions = []
for b in encoded_bytes:
    byte_expressions.append(to_julesprak(b))

joined_bytes = COMMA.join(byte_expressions)

payload = f"{BYTES}{LPAREN}{LBRACKET}{joined_bytes}{RBRACKET}{RPAREN}.{DECODE}{LPAREN}{RPAREN}"

print(payload)
```

## Running the Solution

1. Generate the payload: `python3 solve.py > payload.txt`
2. Send to server: `ncat --ssl julesprak-fengsel.julec.tf 1337 < payload.txt`

**Flag:** `JUL{Jul3språk_j3g_h4r_s4vn3t_d3g_5ånn!}`

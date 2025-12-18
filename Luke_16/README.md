# Out of Bounds

**Author**: Tweey, Shirajuki & olefredrik
**Description**:
>Noen fikk tilgang til Minecraft-serveren vår, men heldigvis ble det ikke gjort noe ugagn. I stedet for å ødelegge noe, ser det ut til at spilleren har etterlatt seg et slags spor. Klarer du å finne ut hva spilleren prøvde å fortelle oss?

**Handout**: [out.pcap](out.pcap)

## Writeup

### 1 Found an interesting payload in the capture

Opened `out.pcap` in Wireshark and looked for the Minecraft traffic (TCP/25565). 

- Right clicked a packet from the main conversation → **Follow** → **TCP Stream**

In the server response stream, there was a chunk of data that i extracted into the file `intresting`.

When skimming `intresting` you can spot several command-like strings (e.g. `/help`, etc.). That made it worth looking closer for patterns.

### 2 Recognize the pattern: lots of `/tp` commands

Among the text, there are many teleport commands on the form:

```http
tp <x> <y> <z>
```

The key observation:

- The `z` values look like a clean sequence: `0, 25, 50, 75, ...`
  - This strongly suggests `z` is being used as an index / ordering field.
- The `x` values fall into printable ASCII ranges (e.g. 74 = `J`, 85 = `U`, 76 = `L`, …)
  - This suggests `x` encodes the message as character codes.

### 3 Decode: sort by `z`, interpret `x` as ASCII

So the decode is:

1. Extract all `tp x y z`
2. Sort by `z`
3. Convert each `x` to `chr(x)`

I made a quick script ([tp.py](tp.py)) to extract the flag.

`tp.py` reads `intresting`, extracts `tp <x> <y> <z>` triples with the regex `\btp\s+(\d+)\s+(\d+)\s+(\d+)\b` de-duplicates (keeps first), sorts by `z`, then converts `x` to characters to produce the hidden message.

**Regex `\btp\s+(\d+)\s+(\d+)\s+(\d+)\b` explained**:

`\b` — word boundary so tp is matched as a separate token (won’t match stp or atp).
`tp` — the literal command.
`\s+` — one-or-more whitespace characters between fields (handles tabs/spaces).
`(\d+)` — capture one-or-more digits (an integer); there are three captures for x, y, z.
trailing `\b` — ensures the last number ends on a word boundary (avoids matching e.g. 123abc).
Using a raw string `(r"…")` in Python avoids needing double backslashes; re.findall returns a list of (x,y,z) tuples in the same order they appear.

Ran it with:

```bash
python3 tp.py
```

### Flag

`JUL{T3lep0Rting_Ar0uND_Th3_w0r1d!?}`
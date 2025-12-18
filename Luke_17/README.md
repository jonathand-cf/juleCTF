# TikTok

**Author**: olefredrik, Shirajuki & Tweey

**Descrition**:
> Cyber har prøvd ut et nytt sosialt medium for å poste videoer. Alt ser tilsynelatende normalt ut, men det gjemmer seg en kode over de tre siste videoene. Klarer du å finne koden? Bruk flaggformatet JUL{kode}. Flagget er case-insensitivt.

## Writeup

I did not like this challange.

### v1.mp4 — Base64 shown in-video

At the very end of the video there is a note with:

```
Cyber! Cyber! Den hemmelige koden er:
Y3liZXI=
```

Decoded:

```bash
printf '%s' 'Y3liZXI=' | base64 -d
```

Result: `cyber`.

### v2.mp4 — Binary (socks) + “morse” (milk cartons)

The video hides two separate encodings:

- **Binary via sock pattern:** `010111110110001001101100`  
  Split into bytes: `01011111 01100010 01101100` → hex `5f 62 6c` → ASCII `_bl`.
- **Morse via milk cartons:** `.. ._. ..__._`  
  In the challenge notation, `l` acts as “dot” and `_` acts as “dash”, giving `IR_` (ends with `_` because the pattern is incomplete).

Combine: `_bl` + `ir_` → `_blir_`.

### v3.mp4 — Crossword word

Mid-video there’s a crossword spelling `influenser` (“influencer” in Norwegian).

## Flag

`cyber` + `_blir_` + `influenser` → `cyber_blir_influenser`  
Flag (case-insensitive): `JUL{cyber_blir_influenser}`.

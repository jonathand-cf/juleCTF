# Cyber Quest for Santa 2

**By Shirajuki**

Cyber, nå ser du sammenhengen.

Oppgavene du har møtt i den digitale verdenen er koblet sammen. Hver utfordring følger faste regler – og noen har bevisst designet dem slik. Rudolf og reinsdyrene holder vakt på hjemmebasen, men det er du som må videre.

Oppdraget er klart: forstå hvordan denne digitale verdenen fungerer, og finn veien dypere inn i systemet. Cyberlandslagsnissen er der ute sted...

---

## Challenge Analysis

The challenge involved a web-based game hosted at `https://cyber-quest-for-santa-2.julec.tf`.

We analyzed the `assets/index-D-H1Dwiy.js` file and identified:

1. **MD5 Hashing**: Island light combinations are hashed with a salt (`Ll`) and compared to target hashes (`Rl`).
2. **AES Decryption**: Correct combinations form a key to decrypt the flag data (`Pl`).

### Extracted Data

- **Salt (`Ll`)**: `Cfpmebtiwqbtvqihqqmi`
- **Target Hashes (`Rl`)**: Defined in the code for islands 2-8.

## Solution

### 1. Light Combinations

We brute-forced the correct color sequences for each island:

- **Island 2**: `redgreenblue`
- **Island 3**: `greenblueredred`
- **Island 4**: `bluegreenredgreenred`
- **Island 2**: `redgreenblue`
- **Island 3**: `greenblueredred`
- **Island 4**: `bluegreenredgreenred`
- **Island 5**: `redbluegreenbluegreen`
- **Island 6**: `greenredbluegreenred`
- **Island 7**: `blueredgreengreen`
- **Island 8**: `bluegreenred`

### 2. Decryption

Concatenating these formed the key:
`redgreenbluegreenblueredredbluegreenredgreenredredbluegreenbluegreengreenredbluegreenredblueredgreengreenbluegreenred`

The flag data (`Pl`) was decrypted using the discovered key and `crypto-js` library. The Salt (`Ll`) was used to derive the key internally by OpenSSL KDF (which CryptoJS uses by default for string keys).

```javascript
const CryptoJS = require("crypto-js");
const key = "redgreenbluegreenblueredredbluegreenredgreenredredbluegreenbluegreengreenredbluegreenredblueredgreengreenbluegreenred";
const Pl = "U2FsdGVkX1/A4CVLNIe1W8ClMhbZj4KfPwecI1SDodPne2PXecVMBgxLzZZYBuvQP4Pau5SyrSqlEHjH6ZRvdVqphn8fKVUU9DO8+2iwXLs=";

// The ciphertext has the Salt embedded (Salted__...) so we just pass the passphrase
const decrypted = CryptoJS.AES.decrypt(Pl, key);
console.log(decrypted.toString(CryptoJS.enc.Utf8));
```

This produced the intermediate string:
`NSB{xk3_o0ex4b_0o3iq_dk3i_3a3ef_b1vkx_e3z3zp3eq_cke1qxz4q}`

### 3. Cipher Decoding

The intermediate string is encoded with a mixed XOR/Leet cipher.

- **Leet**: `0`=o, `1`=i, `3`=e, `4`=a
- **XOR Keys**:
  - `x`->`t` (XOR 12)
  - `k`->`h` (XOR 3)
  - `e,z,a` -> `r,m,v` (XOR 23)
  - `o,f` -> `p,y` (XOR 31)
  - `d` -> `w` (XOR 19)
  - `v` -> `g` (XOR 17)
  - `b,p,B` -> `l,b,L` (XOR 14)

Decoding this produces the plaintext:
`JUL{the_portal_opens_when_every_light_remembers_christmas}`

Applying the game's Leet format for the final flag:

**Final Flag:**
`JUL{th3_p0rt4l_0p3ns_wh3n_3v3ry_l1ght_r3m3mb3rs_chr1stm4s}`

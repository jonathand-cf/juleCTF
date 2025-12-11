# Geogebratreet - CTF Writeup

**Challenge Name:** Geogebratreet  
**Author:** olefredrik  
**Category:** Cryptography / Reverse Engineering  
**Difficulty:** Medium-Hard  

## Challenge Description

> Nå har vi vasket gulvet, og vi har bært ved. Vi har satt opp fuglebånd, så det eneste som mangler er å pynte treet.
>
> Jeg har satt opp noen skisser i GeoGebra om hvor på treet julekulene skal være, basert på flagget. Jeg har lagret posisjonen til julekulene i faktiske_julekuler.txt, men har mistet selve flagget. Heldigvis har jeg backup av testfilen min geogebratreet.ggb som viser hvordan posisjonen til julekulene regnes ut.
>
> Kan du hjelpe meg med å få flagget tilbake?
>
> OBS: Oppgaven er laget i Geogebra 5 Classic. Andre versjoner kan være at ikke er 100% kompatible

## Files Provided

- `geogebratreet.ggb` - GeoGebra file containing the encoding mechanism
- `faktiske_julekuler.txt` - Text file with 61 coordinate pairs representing ornament positions

## Initial Analysis

### Extracting GeoGebra File

After using GeoGebra 5 Classic a while and playing around, it kept crashing and looking it up, GeoGebra files are ZIP archives. I can therefore extract the contents:

```bash
unzip geogebratreet.ggb -d ggb_extracted
```

The main file of interest is `geogebra.xml`, which contains all the mathematical definitions and logic.

### Understanding the Encoding

Examining `geogebra.xml` reveals the encoding process:

#### 1. Christmas Tree Polygon

A 15-sided polygon defining the tree shape:

```javascript
hjørner := {(-2, -2), (2, -2), (2, 2), (10, 2), (4, 10), 
            (8, 10), (2, 18), (6, 18), (0, 26), (-6, 18),
            (-2, 18), (-8, 10), (-4, 10), (-10, 2), (-2, 2)}
```

- **Total perimeter:** 104 units
- **Edge lengths:** `[4, 4, 8, 10, 4, 10, 4, 10, 10, 4, 10, 4, 10, 8, 4]`

#### 2. Flag Encoding Logic

```javascript
// Convert flag to bytes and reverse
flaggBytes := Reverse(TextToUnicode("JUL{falskt_flagg}"))

// Convert to large integer (base-256)
flaggSomHeltall := Sum(flaggBytes(n) * 256^(n-1), n, 1, Length(flaggBytes))

// 61 prime numbers
primtall := {2, 3, 5, 7, 11, 13, 17, 19, ..., 277, 281, 283}

// Map ornaments based on fractional parts
Julekuler := Sequence(gåRundtJuletreet(flaggSomHeltall / primtall(n)), n, 1, 61)
```

#### 3. Key Function: `gåRundtJuletreet(x)`

This function takes a number `x` and:

1. Extracts the fractional part: `desimaler(x) = x - floor(x)`
2. Maps it to a position on the tree perimeter
3. Returns the (x, y) coordinate at that position

The crucial insight: **Each ornament position encodes `flaggSomHeltall mod prime[i]` as a fraction of that prime!**

## Solution Approach

This is a **Chinese Remainder Theorem (CRT)** problem!

### Step-by-Step Solution

1. **Parse ornament coordinates** from `faktiske_julekuler.txt`
2. **Reverse the mapping** - for each ornament:
   - Determine which edge of the polygon it lies on
   - Calculate its fractional distance along the total perimeter
3. **Extract remainders**:
   - `remainder[i] = round(fraction[i] * prime[i]) mod prime[i]`
4. **Apply CRT** to solve the system:
   - `flaggSomHeltall ≡ remainder[i] (mod prime[i])` for all i = 1 to 61
5. **Convert back to flag**:
   - Extract bytes from the integer (little-endian)
   - Reverse the byte array
   - Convert to ASCII string

## Implementation

### Solver Script

Created `solve.py` with the following key components:

```python
from fractions import Fraction

# Define polygon geometry
hjorner = [(-2, -2), (2, -2), (2, 2), (10, 2), (4, 10), 
           (8, 10), (2, 18), (6, 18), (0, 26), (-6, 18),
           (-2, 18), (-8, 10), (-4, 10), (-10, 2), (-2, 2)]

kantLengder = [4, 4, 8, 10, 4, 10, 4, 10, 10, 4, 10, 4, 10, 8, 4]
omkrets = 104

# Prime numbers from GeoGebra
primtall = [2, 3, 5, 7, 11, 13, ..., 277, 281, 283]  # 61 primes

def find_edge_and_position(point):
    """Map coordinate to fractional perimeter position"""
    # ... (edge detection and interpolation logic)

def chinese_remainder_theorem(remainders):
    """Solve system of congruences using CRT"""
    total = 0
    prod = 1
    for modulus, _ in remainders:
        prod *= modulus
    
    for modulus, remainder in remainders:
        p = prod // modulus
        total += remainder * mod_inverse(p, modulus) * p
    
    return total % prod

def mod_inverse(a, m):
    """Extended Euclidean algorithm for modular inverse"""
    # ... (implementation)
```

### Execution

```bash
python3 solve.py
```

### Key Results

```txt
Found 61 ornaments
Expected 61 ornaments (one per prime)

Recovering remainders modulo each prime...
Prime   2: remainder =   1 (frac = 0.500000)
Prime   3: remainder =   2 (frac = 0.666667)
Prime   5: remainder =   2 (frac = 0.400000)
...
Prime 283: remainder =  72 (frac = 0.254417)

Applying Chinese Remainder Theorem...
flaggSomHeltall = 2928877139081545338140742645383966936184023271451565235727297282282889377187382378887931166636030321721124554773066877

Converting to bytes and reversing...

FLAG: JUL{så_gjør_v1_5å_når_vi_går_rundt_geogebratre3t}
```

## Flag

```txt
JUL{så_gjør_v1_5å_når_vi_går_rundt_geogebratre3t}
```

**Translation:** "JUL{so that's what we do when we walk around the geogebratree}"

## Takeaways

1. GeoGebra files are ZIP archives - always extract and examine XML (Geogebra 5 Classic is useless)
2. Fractional parts can encode modular remainders elegantly
3. CRT is powerful for reconstructing values from multiple modular constraints
4. Norwegian Christmas-themed crypto challenges are delightful! 🎄

## Tools Used

- Python 3 with `fractions` module
- Text editor for XML analysis
- Command line utilities (`unzip`)
- GeoGebra 5 Classic

---

**Solver:** [solve.py](solve.py) 
**AI Helper for solver** [Claude 4.5 Sonnet](https://claude.ai/)

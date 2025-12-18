
cipher = "NSB{cfp3e_esw0bok_4iw_e31iw33eq_e1w1iv_xk3_wtx4qxe34z}"

# Mappings deduced:
# Digits -> Leet
# Chars -> XOR with specific keys (or direct mapping)

mapping = {
    '0': 'o',
    '1': 'i',
    '3': 'e',
    '4': 'a',
    '_': '_',
    '{': '{',
    '}': '}',
    # Prefix
    'N': 'J',
    'S': 'U',
    'B': 'L',
    
    # Body
    'c': 'c',
    'f': 'y',
    'p': 'b',
    'e': 'r',
    's': 'u',
    'w': 'd',
    'b': 'l',
    'o': 'p',
    'k': 'h',
    'i': 'n',
    'q': 's',
    'v': 'g',
    'x': 't',
    't': 'a',
    'z': 'm'
}

decoded = []
for char in cipher:
    if char in mapping:
        decoded.append(mapping[char])
    else:
        # Fallback or error
        decoded.append(f"[{char}]")

flag = "".join(decoded)
print(f"Decoded Flag: {flag}")

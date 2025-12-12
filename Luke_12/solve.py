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
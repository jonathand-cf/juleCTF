import sys
# Length: 746 (optimized with ai, originally was 2800+)

# Julespråk primitives
ONE = "🏂" # 1
ZERO = "🥶" # 0
LPAREN = "🎈"
RPAREN = "🎇"
AND = "&"
OR = "|"
XOR = "^"
ADD = "+"
SUB = "-"
MUL = "*"
LSHIFT = "<<"
RSHIFT = ">>"
NOT = "~"
POW = "**"
FLOORDIV = "//"
MOD = "%"

# Function aliases
LEN = "🥛"
# STR = "🧣"  # Forbidden!
TRUE = "🏂"
FALSE = "🥶"
BYTES = "🦌"
RANGE = "🎿"
PRINT = "🎁"

# Constants
LBRACKET = "🎉"
RBRACKET = "🎊"
COMMA = "🎺"
DECODE = "📜"

# Precedence levels
PREC = {
    "leaf": 100,
    "**": 95,
    "~": 90,
    "*": 70, "/": 70, "%": 70, "//": 70,
    "+": 60, "-": 60,
    "<<": 50, ">>": 50,
    "&": 40,
    "^": 30,
    "|": 20,
}

found = {}

def add_entry(val, expr, prec, is_constant=False):
    cost = len(expr)
    if val not in found or cost < found[val][0]:
        found[val] = (cost, expr, prec, is_constant)
        return True
    return False

# Base simple numbers
add_entry(0, ZERO, PREC["leaf"], is_constant=True)
add_entry(1, ONE, PREC["leaf"], is_constant=True)
add_entry(-1, f"{NOT}{ZERO}", PREC["~"], is_constant=True)
expr_list_1 = f"{LEN}{LPAREN}{LBRACKET}{ZERO}{RBRACKET}{RPAREN}"
MAX_VAL = 255
import itertools
changed = True
while changed:
    changed = False
    
    # Sort keys by cost
    current_items = sorted(found.items(), key=lambda x: x[1][0])
    
    # Unary ops
    for val, (cost, expr, prec, _) in current_items:
        operand = expr
        if prec < PREC["~"]:
            operand = f"{LPAREN}{expr}{RPAREN}"
        
        res = ~val
        new_expr = f"{NOT}{operand}"
        if add_entry(res, new_expr, PREC["~"]):
            changed = True

    # Binary ops
    # Increase cutoff
    
    for (v1, data1), (v2, data2) in itertools.product(current_items, repeat=2):
        c1, e1, p1, _ = data1
        c2, e2, p2, _ = data2
        
        if c1 + c2 > 50: continue 
        
        ops = [
            (v1 + v2, "+"),
            (v1 - v2, "-"),
            (v1 * v2, "*"),
            (v1 * v2, "*"), # Commutativity handled by product order, but * is same.
            (v1 ^ v2, "^"),
            (v1 | v2, "|"),
            (v1 & v2, "&"),
        ]
        
        # Extended ops
        if v2 != 0:
             ops.append((v1 // v2, "//"))
             ops.append((v1 % v2, "%"))
        
        # Shifts
        if 0 <= v2 < 16:
             ops.append((v1 << v2, "<<"))
             ops.append((v1 >> v2, ">>"))

        # Power (careful with size)
        if 2 <= v1 <= 20 and 2 <= v2 <= 10:
             try:
                 res_pow = v1 ** v2
                 if -MAX_VAL <= res_pow <= MAX_VAL:
                     ops.append((res_pow, "**"))
             except:
                 pass

        for res, op in ops:
            if not (-MAX_VAL <= res <= MAX_VAL): continue
            
            # Formatting logic
            # Left operand
            s1 = e1
            needs_parens_left = False
            if p1 < PREC[op]:
                needs_parens_left = True
            
            if needs_parens_left:
                s1 = f"{LPAREN}{e1}{RPAREN}"
                
            # Right operand
            s2 = e2
            needs_parens_right = False
            if p2 < PREC[op]:
                needs_parens_right = True
            elif p2 == PREC[op]:
                if op == "**":
                    if op == "**": needs_parens_left = True
                else:
                    if op not in ["+", "*", "&", "|", "^"]: 
                        needs_parens_right = True
            
            if op == "**" and p1 == PREC["**"]:
                 s1 = f"{LPAREN}{e1}{RPAREN}"

            if needs_parens_right:
                s2 = f"{LPAREN}{e2}{RPAREN}"
                
            expr_str = f"{s1}{op}{s2}"
            if add_entry(res, expr_str, PREC[op]):
                changed = True

# Generate payload
target = "Julespråk er favorittspråket mitt!"
encoded_bytes = target.encode('utf-8')

byte_exprs = []
for b in encoded_bytes:
    if b in found:
        byte_exprs.append(found[b][1])
    else:
        print(f"Error: Byte {b} not found!", file=sys.stderr)
        sys.exit(1)

joined = COMMA.join(byte_exprs)
payload = f"{BYTES}{LPAREN}{LBRACKET}{joined}{RBRACKET}{RPAREN}.{DECODE}{LPAREN}{RPAREN}"

print(payload)
print(f"Length: {len(payload)}", file=sys.stderr)
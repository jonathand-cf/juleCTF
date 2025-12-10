#!/usr/bin/env python3
"""
CTF Challenge: GeoGebra Christmas Tree Flag Recovery

The encoding mechanism:
1. Flag is converted to unicode bytes and reversed: flaggBytes = Reverse(TextToUnicode(flag))
2. Bytes converted to large integer: flaggSomHeltall = Sum(flaggBytes(n) * 256^(n-1), n, 1, Length(flaggBytes))
3. For each prime: Julekuler[i] = gåRundtJuletreet(flaggSomHeltall / prime[i])
4. gåRundtJuletreet maps fractional part to position on tree polygon

To reverse:
1. For each ornament position, find which edge it's on
2. Calculate the fractional distance along the perimeter (andelLengde)
3. This is the fractional part of (flaggSomHeltall / prime[i])
4. Use Chinese Remainder Theorem or similar to recover flaggSomHeltall
5. Convert back to bytes and reverse to get flag
"""

from fractions import Fraction
from typing import List, Tuple

# Christmas tree polygon corners (from GeoGebra XML)
hjorner = [
    (-2, -2), (2, -2), (2, 2), (10, 2), (4, 10), 
    (8, 10), (2, 18), (6, 18), (0, 26), (-6, 18),
    (-2, 18), (-8, 10), (-4, 10), (-10, 2), (-2, 2)
]

# Edge lengths of the polygon
kantLengder = [4, 4, 8, 10, 4, 10, 4, 10, 10, 4, 10, 4, 10, 8, 4]

# Cumulative lengths
kummulativLengde = [0, 4, 8, 16, 26, 30, 40, 44, 54, 64, 68, 78, 82, 92, 100, 104]

# Total perimeter
omkrets = 104

# Fraction of total perimeter at each corner
andelLengde = [Fraction(x, omkrets) for x in kummulativLengde]

# Prime numbers (from GeoGebra XML)
primtall = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149, 151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229, 233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283]

def interpoler(node1: Tuple[float, float], node2: Tuple[float, float], d1: float) -> Tuple[float, float]:
    """Linear interpolation between two nodes"""
    x = node1[0] * (1 - d1) + node2[0] * d1
    y = node1[1] * (1 - d1) + node2[1] * d1
    return (x, y)

def find_edge_and_position(point: Tuple[Fraction, Fraction]) -> Fraction:
    """
    Given a point on the tree perimeter, find which edge it's on and 
    calculate the fractional distance along the total perimeter.
    
    Returns the fraction (andelLengde value) representing position on tree.
    """
    x, y = point
    
    # Check each edge
    for i in range(len(hjorner)):
        node1 = hjorner[i]
        node2 = hjorner[(i + 1) % len(hjorner)]
        
        # Check if point is on this edge (collinear and between nodes)
        # Line from node1 to node2: parametric form
        # P = node1 + t * (node2 - node1), where 0 <= t <= 1
        
        dx = node2[0] - node1[0]
        dy = node2[1] - node1[1]
        
        # Solve for t
        if dx != 0:
            t = Fraction(x - node1[0]) / Fraction(dx)
        elif dy != 0:
            t = Fraction(y - node1[1]) / Fraction(dy)
        else:
            continue  # Degenerate edge
        
        # Check if t is valid and point is on edge
        if 0 <= t <= 1:
            # Verify point is actually on the line
            expected_x = Fraction(node1[0]) + t * Fraction(dx)
            expected_y = Fraction(node1[1]) + t * Fraction(dy)
            
            if abs(expected_x - x) < Fraction(1, 1000000) and abs(expected_y - y) < Fraction(1, 1000000):
                # We found the edge! Calculate position along perimeter
                edge_start_fraction = andelLengde[i]
                edge_end_fraction = andelLengde[i + 1]
                
                position = edge_start_fraction + t * (edge_end_fraction - edge_start_fraction)
                return position
    
    # If not found on any edge, might be at a corner
    for i, corner in enumerate(hjorner):
        if abs(x - corner[0]) < Fraction(1, 1000000) and abs(y - corner[1]) < Fraction(1, 1000000):
            return andelLengde[i]
    
    raise ValueError(f"Point ({x}, {y}) not found on tree perimeter")

def read_julekuler(filename: str) -> List[Tuple[Fraction, Fraction]]:
    """Read the Christmas ornament positions from file"""
    with open(filename, 'r') as f:
        content = f.read()
    
    # Extract the set of coordinates
    # Format: Julekuler:={(x1, y1), (x2, y2), ...}
    start = content.find('{')
    end = content.find('}')
    coords_str = content[start+1:end]
    
    # Parse coordinates
    julekuler = []
    coords = coords_str.split('), (')
    for coord in coords:
        coord = coord.strip('()').strip()
        parts = coord.split(', ')
        
        # Parse fractions
        x_str = parts[0].strip()
        y_str = parts[1].strip()
        
        # Convert to Fraction
        if '/' in x_str:
            x = Fraction(x_str.replace(' ', ''))
        else:
            x = Fraction(int(x_str))
        
        if '/' in y_str:
            y = Fraction(y_str.replace(' ', ''))
        else:
            y = Fraction(int(y_str))
        
        julekuler.append((x, y))
    
    return julekuler

def chinese_remainder_theorem(remainders):
    """
    Solve system of congruences using Chinese Remainder Theorem:
    x ≡ a_i (mod n_i) for all i
    
    Args:
        remainders: List of tuples (modulus, remainder)
    
    Returns:
        The solution x modulo the product of all moduli
    """
    total = 0
    prod = 1
    for modulus, _ in remainders:
        prod *= modulus
    
    for modulus, remainder in remainders:
        p = prod // modulus
        # Find modular inverse of p modulo modulus
        total += remainder * mod_inverse(p, modulus) * p
    
    return total % prod

def mod_inverse(a, m):
    """Find modular inverse of a modulo m using extended Euclidean algorithm"""
    def extended_gcd(a, b):
        if a == 0:
            return b, 0, 1
        gcd, x1, y1 = extended_gcd(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y
    
    gcd, x, _ = extended_gcd(a % m, m)
    if gcd != 1:
        raise ValueError("Modular inverse does not exist")
    return (x % m + m) % m

def main():
    # Read the actual ornament positions
    julekuler = read_julekuler('faktiske_julekuler.txt')
    
    print(f"Found {len(julekuler)} ornaments")
    print(f"Expected {len(primtall)} ornaments (one per prime)")
    
    # For each ornament, find its fractional position
    fractional_parts = []
    for i, ornament in enumerate(julekuler):
        try:
            fraction = find_edge_and_position(ornament)
            fractional_parts.append(fraction)
        except ValueError as e:
            print(f"Error with ornament {i+1}: {e}")
            fractional_parts.append(None)
    
    print("\n" + "="*60)
    print("Recovering remainders modulo each prime...")
    
    # Recover remainders
    remainders = []
    for i, (prime, frac) in enumerate(zip(primtall, fractional_parts)):
        if frac is not None:
            # The remainder when dividing flaggSomHeltall by prime
            # Since desimaler(flaggSomHeltall / prime) = frac
            # We have: (flaggSomHeltall mod prime) / prime ≈ frac
            # So: flaggSomHeltall mod prime ≈ frac * prime
            remainder = (frac * prime) % prime
            # Round to nearest integer
            remainder_int = int(remainder + Fraction(1, 2))
            if remainder_int >= prime:
                remainder_int = prime - 1
            remainders.append((prime, remainder_int))
            print(f"Prime {prime:3d}: remainder = {remainder_int:3d} (frac = {float(frac):.6f})")
    
    print("\n" + "="*60)
    print("Applying Chinese Remainder Theorem...")
    
    # Use CRT to recover flaggSomHeltall
    flaggSomHeltall = chinese_remainder_theorem(remainders)
    
    print(f"flaggSomHeltall = {flaggSomHeltall}")
    print(f"In scientific notation: {float(flaggSomHeltall):.6e}")
    
    # Convert back to bytes
    print("\n" + "="*60)
    print("Converting to bytes and reversing...")
    
    # Extract bytes (little-endian, reversed in the encoding)
    flag_bytes = []
    temp = flaggSomHeltall
    while temp > 0:
        flag_bytes.append(temp % 256)
        temp //= 256
    
    # Reverse to get original order
    flag_bytes.reverse()
    
    # Convert to string
    try:
        flag = ''.join(chr(b) for b in flag_bytes)
        print(f"\n{'='*60}")
        print(f"FLAG RECOVERED: {flag}")
        print(f"{'='*60}")
    except ValueError as e:
        print(f"Error converting bytes to string: {e}")
        print(f"Bytes: {flag_bytes}")
    
if __name__ == "__main__":
    main()

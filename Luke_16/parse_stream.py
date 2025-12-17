import sys
import binascii
import base64
import zlib

def parse_hex_stream(filename):
    # Parse tshark raw hex output
    # Look for indented lines (Node 1 -> Client, usually)
    # Actually, tshark output format for raw:
    # Node 0: ...
    # Node 1: ...
    # Then data.
    # The indentation indicates direction.
    # But I can also just search the whole stream if I assume the data is only sent one way.
    
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    full_hex = ""
    for line in lines:
        stripped = line.strip()
        if not stripped: continue
        if stripped.startswith("="): continue
        if "Node" in stripped: continue
        if "Follow" in stripped: continue
        if "Filter" in stripped: continue
        
        # Check indentation for direction?
        # Stream raw output from tshark -z usually:
        # 00000000  (hex)
        # Wait, I used -z follow,tcp,raw,0.
        # It outputs hex strings directly.
        # Indented means Server -> Client (Node 1).
        # Check for tab or multiple spaces
        if line.startswith('\t') or line.startswith(' '):
             full_hex += stripped
        else:
             # Client -> Server
             # We assume we want Server -> Client
             pass
             
    return full_hex

def extract_blobs(full_hex):
    # Convert to bytes
    try:
        data = binascii.unhexlify(full_hex)
    except Exception as e:
        print(f"Error unhexlifying: {e}")
        return []

    # Search for M) (0x4d 0x29)
    # The blobs seem to be Base64 strings.
    # So we look for b'M)' followed by printable ascii
    
    blobs = []
    
    start_marker = b'M)'
    start = 0
    while True:
        idx = data.find(start_marker, start)
        if idx == -1:
            break
        
        # Found M)
        # Extract until end of Base64 string
        # Base64 chars: A-Z a-z 0-9 + / =
        # We'll just read until a non-base64 char
        
        content = b""
        curr = idx + 2 # Skip M)
        while curr < len(data):
            c = data[curr]
            # Check if valid base64
            is_b64 = (0x41 <= c <= 0x5a) or \
                     (0x61 <= c <= 0x7a) or \
                     (0x30 <= c <= 0x39) or \
                     c == 0x2b or c == 0x2f or c == 0x3d
            if is_b64:
                content += bytes([c])
                curr += 1
            else:
                break
        
        if len(content) > 10: # Minimum valid length to care
             blobs.append(content)
             print(f"Found blob at {idx}: {content[:20]}... (Len: {len(content)})")
        
        start = curr
        
    return blobs

hex_data = parse_hex_stream('stream1.hex')
print(f"Total hex stream size: {len(hex_data)//2} bytes")

blobs = extract_blobs(hex_data)
print(f"Found {len(blobs)} blobs")

all_decoded = b""
for i, b in enumerate(blobs):
    try:
        decoded = base64.b64decode(b)
        all_decoded += decoded
        # Check Zlib
        if decoded.startswith(b'\x78\x9c') or decoded.startswith(b'\x78\x68'):
            print(f"Blob {i} has Zlib header {decoded[:2].hex()}!")
    except Exception as e:
        print(f"Blob {i} decode error: {e}")

print(f"Total decoded size: {len(all_decoded)}")
with open('reassembled_flag.bin', 'wb') as f:
    f.write(all_decoded)

# Try full decompression
try:
    z = zlib.decompress(all_decoded)
    print("Full decompression success!")
    with open('flag_content.bin', 'wb') as f:
        f.write(z)
except Exception as e:
    print(f"Full decompression failed: {e}")
    # Try decompressing individual blobs or starting from Blob with Zlib header

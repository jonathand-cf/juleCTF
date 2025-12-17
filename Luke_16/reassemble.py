import subprocess
import binascii
import zlib
import base64

def get_frames():
    # Use tshark to get frame data and time using tcp.payload
    # We look for hex 4d29 (M))
    cmd = [
        "tshark", "-r", "out.pcap",
        "-Y", "frame contains 4d:29",
        "-T", "fields",
        "-e", "frame.number",
        "-e", "frame.time_epoch",
        "-e", "tcp.payload"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    frames = []
    
    seen_payloads = set()

    for line in result.stdout.splitlines():
        parts = line.split('\t')
        if len(parts) < 3: continue
        frame_num, epoch, payload_hex = parts
        
        # Payload might be empty or invalid
        if not payload_hex or len(payload_hex) < 4: continue
        
        # Remove colons if present (tshark fields usually don't have colons for -e hex)
        payload_hex = payload_hex.replace(':', '')
        
        # Check for duplicates
        if payload_hex in seen_payloads:
            continue
        seen_payloads.add(payload_hex)
        
        # Find M) (4d29) start
        # We assume the message starts with 4d29
        idx = payload_hex.find('4d29')
        if idx == -1:
            continue
            
        # Extract content after 4d29
        # The content is Base64 string encoded in Hex
        # So we need to convert Hex -> Bytes (which is the Base64 string) -> Decode Base64 -> Binary
        
        # Hex '4e' is 'N'.
        # payload_hex[idx+4:] is the hex of the base64 string
        base64_hex = payload_hex[idx+4:]
        
        try:
            base64_bytes = binascii.unhexlify(base64_hex)
            
            # Clean up: Base64 string might end with newline or garbage
            # We take chars until first non-base64 char?
            # Or just strip()
            base64_str = base64_bytes.split(b'\r')[0].split(b'\n')[0]
            
            decoded = base64.b64decode(base64_str, validate=False)
            
            frames.append({
                'id': frame_num,
                'time': float(epoch),
                'data': decoded,
                'header': decoded[:10].hex()
            })
            print(f"Frame {frame_num}: Found {len(decoded)} bytes. Header: {decoded[:10].hex()}")
            
        except Exception as e:
            print(f"Error parsing frame {frame_num}: {e}")
            
    return frames

frames = get_frames()
print(f"Found {len(frames)} unique M) messages")

# Sort by time
frames.sort(key=lambda x: x['time'])

# Concatenate data
full_data = b"".join([f['data'] for f in frames])
print(f"Total reassembled size: {len(full_data)}")

# Try Decompress (Zlib)
try:
    # Try standard zlib
    decompressed = zlib.decompress(full_data)
    print("Success! Decompressed zlib data.")
    with open('flag_data_zlib.bin', 'wb') as f:
        f.write(decompressed)
except Exception as e:
    print(f"Decompression failed: {e}")
    
    # Try identifying if any chunk is a Zlib header and try decompressing from there
    # It's possible the first chunk matches Frame X
    for i, f in enumerate(frames):
        if f['data'].startswith(b'\x78'):
             print(f"Potential Zlib start at Frame {f['id']} (Index {i})")
             # Try decompressing starting from this frame
             partial_data = b"".join([frames[j]['data'] for j in range(i, len(frames))])
             try:
                 d = zlib.decompress(partial_data)
                 print(f"  -> Success! Decompressed from Index {i}")
                 with open('flag_data_zlib.bin', 'wb') as f:
                     f.write(d)
                 break
             except Exception as ez:
                 print(f"  -> Failed: {ez}")

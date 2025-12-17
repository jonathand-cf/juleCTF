import binascii
import base64
import zlib

def inspect_stream(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
        
    full_b64 = ""
    for line in lines:
        parts = line.strip().split('\t')
        if len(parts) < 2: continue
        
        # tshark -T fields -e tcp.seq -e tcp.payload
        # parts[0] is seq, parts[1] is payload
        payload_hex = parts[1].replace(':', '')
        try:
            payload = binascii.unhexlify(payload_hex)
            # Try to decode as ascii
            try:
                txt = payload.decode('ascii')
                # Check if it looks like base64
                # It might be fragments.
                # Let's verify character set
                if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in txt):
                    full_b64 += txt
                    # print(f"Packet {parts[0]}: Base64 chunk len {len(txt)}")
                else:
                    print(f"Packet {parts[0]}: Non-Base64: {repr(txt[:50])}")
            except:
                print(f"Packet {parts[0]}: Binary data len {len(payload)}")
                
        except Exception as e:
            pass
            
    print(f"Total Base64 collected: {len(full_b64)}")
    return full_b64

b64_data = inspect_stream('stream1_server.txt')

if len(b64_data) > 0:
    try:
        raw = base64.b64decode(b64_data)
        print(f"Decoded size: {len(raw)}")
        
        # Try zlib
        try:
            z = zlib.decompress(raw)
            print("Zlib success!")
            with open('flag_image.bin', 'wb') as f:
                f.write(z)
        except:
            print("Zlib failed. Saving raw.")
            with open('flag_image.bin', 'wb') as f:
                f.write(raw)
                
    except Exception as e:
        print(f"Base64 decode failed: {e}")


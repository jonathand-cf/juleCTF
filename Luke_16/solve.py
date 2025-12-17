import base64
import math
from PIL import Image

try:
    with open('blobs.txt', 'r') as f:
        lines = f.readlines()

    all_data = b""
    for i, line in enumerate(lines):
        content = line.strip()
        if content.startswith("M)"):
            content = content[2:]
        
        try:
            decoded = base64.b64decode(content)
            all_data += decoded
            print(f"Blob {i}: {len(decoded)} bytes")
        except Exception as e:
            print(f"Blob {i}: Error decoding: {e}")

    print(f"Total data size: {len(all_data)} bytes")
    
    # Try 128 width (Minecraft map standard)
    width = 128
    height = int(math.ceil(len(all_data) / width))
    
    print(f"Creating {width}x{height} image")
    
    # Pad data if necessary
    padded_data = all_data
    if len(all_data) < width * height:
        padded_data += b'\x00' * (width * height - len(all_data))
        
    img = Image.frombytes('P', (width, height), padded_data)
    
    # Create a simplified palette (Minecraft map colors approximate)
    # Actually, let's just use a grayscale or rainbow palette to distinguish values
    palette = []
    for i in range(256):
        # r, g, b
        palette.extend((i, i, i))
    img.putpalette(palette)
    
    img.save('output_128.png')
    
    # Resize for better visibility
    img_large = img.resize((width*4, height*4), Image.NEAREST)
    img_large.save('output_128_large.png')
    
    # Also try analyzing the values. Are they in a specific range?
    offset_counts = {}
    for b in all_data:
        offset_counts[b] = offset_counts.get(b, 0) + 1
    
    # print most common bytes
    sorted_counts = sorted(offset_counts.items(), key=lambda x: x[1], reverse=True)
    print("Top 10 byte values:", sorted_counts[:10])

except Exception as e:
    print(f"Error: {e}")

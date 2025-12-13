
# Scan binary for patterns: string + null + emoji (utf-8 4 bytes starts with 0xF0)
# Binary path: handout/app/julesprak

import re

with open("handout/app/julesprak", "rb") as f:
    data = f.read()

# Pattern: [printable chars]+ \x00 \xF0 \x9F ...
# Emojis usually 4 bytes: F0 9F xx xx
regex = re.compile(b'([a-zA-Z_0-9]+)\x00(\xf0\x9f[\x80-\xbf]{2})')

matches = regex.findall(data)

print("Found mappings:")
for name, emoji in matches:
    try:
        name_str = name.decode()
        emoji_str = emoji.decode()
        print(f"{name_str} -> {emoji_str}")
    except:
        print(f"{name} -> {emoji}")

# Also check for 3-byte emojis just in case
regex3 = re.compile(b'([a-zA-Z_0-9]+)\x00(\xe2[\x80-\xbf]{2})')
matches3 = regex3.findall(data)
for name, emoji in matches3:
    try:
        print(f"{name.decode()} -> {emoji.decode()}")
    except:
        pass
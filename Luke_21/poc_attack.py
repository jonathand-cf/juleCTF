# patch_p12.py
import sys

def read_len(buf, i):
    first = buf[i]
    if first < 0x80:
        return first, 1
    n = first & 0x7F
    val = 0
    for b in buf[i+1:i+1+n]:
        val = (val << 8) | b
    return val, 1 + n

def read_tlv(buf, i):
    tag = buf[i]; i += 1
    ln, ln_size = read_len(buf, i); i += ln_size
    content_start = i
    next_offset = content_start + ln
    return tag, ln, content_start, next_offset

def main(src, dst):
    data = bytearray(open(src, 'rb').read())

    # root SEQUENCE
    tag, ln, content_start, next_offset = read_tlv(data, 0)
    if tag != 0x30:
        raise SystemExit("Not a SEQUENCE at root")
    off = content_start  # step into root content

    # version
    _, _, _, off = read_tlv(data, off)
    # authSafe ContentInfo
    _, _, _, off = read_tlv(data, off)
    # macData starts at current off
    if off >= len(data):
        raise SystemExit("No third child found")
    if data[off] != 0x30:
        print(f"Warning: third child tag is 0x{data[off]:02x}, patching anyway")
    data[off] = 0xA0

    open(dst, 'wb').write(data)
    print(f"patched -> {dst}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(f"Usage: {sys.argv[0]} legit.p12 patched.p12")
    main(sys.argv[1], sys.argv[2])

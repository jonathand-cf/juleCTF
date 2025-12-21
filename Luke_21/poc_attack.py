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

def patch(src, dst):
    data = bytearray(open(src,'rb').read())
    tag, ln, content_start, _ = read_tlv(data, 0)
    if tag != 0x30:
        raise SystemExit('root not SEQUENCE')
    off = content_start
    _, _, _, off = read_tlv(data, off)  # version
    _, _, _, off = read_tlv(data, off)  # authSafe
    if off >= len(data):
        raise SystemExit('no third child')
    data[off] = 0xA0
    open(dst,'wb').write(data)

patch('new_legit.p12','new_patched.p12')
print('wrote new_patched.p12')
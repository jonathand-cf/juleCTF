set -euo pipefail
# regenerate
rm -f ca.key ca.crt ca.srl wayne.key wayne.csr wayne.crt new_legit.p12 new_patched.p12
openssl genrsa -out ca.key 2048 >/dev/null 2>&1
openssl req -new -x509 -key ca.key -days 365 -out ca.crt -subj "/CN=santaclaus" >/dev/null 2>&1
openssl genrsa -out wayne.key 2048 >/dev/null 2>&1
openssl req -new -key wayne.key -out wayne.csr -subj "/CN=wayne" >/dev/null 2>&1
openssl x509 -req -in wayne.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out wayne.crt -days 365 >/dev/null 2>&1
openssl pkcs12 -export -inkey wayne.key -in wayne.crt -certfile ca.crt -name "wayne" -passout pass:pass -keypbe NONE -certpbe NONE -out new_legit.p12 >/dev/null 2>&1
python3 - <<'PY'
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
PY

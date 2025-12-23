import base64
key = base64.b64decode('kc86vOFEczPvg1R3ZGcaYtlqq2cev5vzRDhJCBfl0dlVpyJW=')
parts = [
    'pRvdn4L+EU9QPmMAQP9HZUO4i8m62CDf+pbxB1ojKMckd+tDmCe=',
    'L9vm9x4Du4awAN21iXJZ3ZWyp31aa0d/M+lLxHI0DJTdUTuUGkF=',
    'qdusWdwPnf6FJAZ/kyVFVnKpRJhzu7rYTs8jneHHQWIigVT3FDb='
]
pt = b''.join(
    bytes(c ^ key[i % len(key)] for i, c in enumerate(base64.b64decode(p)))
    for p in parts
)
print(pt.decode())  # -> your flag, starts with JUL{...}

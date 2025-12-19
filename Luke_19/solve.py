import base64, uuid
rid = "5054092d-0610-c773-6dbd-e23c342e4c29"
b = uuid.UUID(rid).bytes_le
print(base64.b64encode(b[:10]).decode())
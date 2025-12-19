import base64, uuid
b = uuid.UUID("12345678-1234-5678-1234-567812345678").bytes_le
print(base64.b64encode(b[:10]).decode())
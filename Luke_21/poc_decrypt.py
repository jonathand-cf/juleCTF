import base64, sys
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

enc_b64 = sys.stdin.read().strip()
cipher = base64.b64decode(enc_b64)
with open("wayne.key","rb") as f:
    key = serialization.load_pem_private_key(f.read(), password=None)
pt = key.decrypt(cipher, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
print(pt.decode())
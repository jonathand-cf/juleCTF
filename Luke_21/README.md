# Luke 21, PKCS#12

**Author**: ciphr
**Description**:
> Do you want to get your packet from santa? Due to new security regulations, all recepients must now show a certificate validating their identity.

## Writeup

PKCS #12 defines an archive file format for storing many cryptography objects as a single file.
The filename extension for PKCS #12 files is `.p12` or `.pfx`.

The [make_p12](make_p12.sh) script is for [CVE-2025-12816](https://github.com/digitalbazaar/forge/security/advisories/GHSA-5gfm-wpxj-wjgq), or its based on that, for that volnerbility.

### How the voln arises

```sh
openssl genrsa -out ca.key 2048
openssl req -new -x509 -key ca.key -days 365 -out ca.crt -subj "/CN=santaclaus"

openssl genrsa -out wayne.key 2048
openssl req -new -key wayne.key -out wayne.csr -subj "/CN=wayne"
openssl x509 -req -in wayne.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out wayne.crt -days 365
```

```sh
openssl pkcs12 -export \
  -inkey wayne.key \
  -in wayne.crt \
  -certfile ca.crt \
  -name "wayne" \
  -passout pass:pass \
  -out legit.p12
```

Then i patch the new_legit.p12:

```bash
✗ bash make_p12.sh
```

and then uploaded the `new_patched.p12` to `api/upload`. 
The response was saved in [response](response.bin).

```base64
IMYpbH2hjYLvThlimlLGzBtLdjYSbJ1t2u5iDZs43gSJ1ZZnQtKn22N/Q6ZmM7Au+HF2Fi+aIxRAHePv3KF3Xoz2uUAhzPc3tvVDmJIPovqSGcmc+xcnl6XNtnp1wUo9YYtW8ggmBA6SAZyogaKg98wEmnQmEtcX9K+AWdHYsX9PRto6fG55UBAG9+e0TCMVTnok5x58w5whsxCL75MkY8+DzA99oEy4G4tEIH+88Lh8YkVFHeRXvyAqmlpAOyEV0sBtheiZFAiQT39FwYRAaw+3iLTi33TtKrQ/xFuIz8lfy6cDei2W4OGk0DXAS9YYOpXXsrPKntQ+DMGcc93pWA==
```

Then i decrypted it with [poc_decrypt](poc_decrypt.py) with the `wayne.key` like:

```sh
cat response.txt | python3 poc_decrypt.py
```

and got the flag `JUL{c3rt1f13d_p4c3t_r3c31v3r}`

### Flag

JUL{c3rt1f13d_p4c3t_r3c31v3r}

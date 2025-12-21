# Luke 21, PKCS#12

**Author**: ciphr
**Description**:
> Do you want to get your packet from santa? Due to new security regulations, all recepients must now show a certificate validating their identity.

## Writeup

PKCS #12 defines an archive file format for storing many cryptography objects as a single file.
The filename extension for PKCS #12 files is `.p12` or `.pfx`.

I looked at the handout service in `handout/pkcs12/app/api/upload/route.ts` and saw it parses uploads with `forge.pkcs12.pkcs12FromAsn1(p12Asn1, true, password)` and a random password (so any MAC must be bypassed).
Then i checked `package.json` / `package-lock.json` and saw `node-forge@1.3.1`, a vulnerable version of the ASN.1 validator (`asn1.validate`) that lets optional fields desync and skip MAC verification.

The [make_p12](make_p12.sh) and then [poc_attack](poc_attack.py) scripts is the [CVE-2025-12816](https://github.com/digitalbazaar/forge/security/advisories/GHSA-5gfm-wpxj-wjgq).

### How the voln arises

First (as in [make_p12](make_p12.sh)) we make the keys:

```sh
openssl genrsa -out ca.key 2048 >/dev/null 2>&1
openssl req -new -x509 -key ca.key -days 365 -out ca.crt -subj "/CN=santaclaus" >/dev/null 2>&1
openssl genrsa -out wayne.key 2048 >/dev/null 2>&1
openssl req -new -key wayne.key -out wayne.csr -subj "/CN=wayne" >/dev/null 2>&1
openssl x509 -req -in wayne.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out wayne.crt -days 365 >/dev/null 2>&1
```

Then export it:

```sh
openssl pkcs12 -export -inkey wayne.key -in wayne.crt -certfile ca.crt -name "wayne" -passout pass:pass -keypbe NONE -certpbe NONE -out new_legit.p12 >/dev/null 2>&1
```

Then i exploit the new_legit.p12:

```bash
✗ python3 poc_attack.py
```

and then uploaded the `new_patched.p12` to `api/upload`.
The response was saved in [response](response.bin).

```base64
IMYpbH2hjYLvThlimlLGzBtLdjYSbJ1t2u5iDZs43gSJ1ZZnQtKn22N/Q6ZmM7Au+HF2Fi+aIxRAHePv3KF3Xoz2uUAhzPc3tvVDmJIPovqSGcmc+xcnl6XNtnp1wUo9YYtW8ggmBA6SAZyogaKg98wEmnQmEtcX9K+AWdHYsX9PRto6fG55UBAG9+e0TCMVTnok5x58w5whsxCL75MkY8+DzA99oEy4G4tEIH+88Lh8YkVFHeRXvyAqmlpAOyEV0sBtheiZFAiQT39FwYRAaw+3iLTi33TtKrQ/xFuIz8lfy6cDei2W4OGk0DXAS9YYOpXXsrPKntQ+DMGcc93pWA==
```

Then i decrypted it with [poc_decrypt](poc_decrypt.py) with my `wayne.key` like:

```sh
cat response.txt | python3 poc_decrypt.py
```

and got the flag `JUL{c3rt1f13d_p4c3t_r3c31v3r}`

### Flag

JUL{c3rt1f13d_p4c3t_r3c31v3r}

set -euo pipefail
# regenerate
rm -f ca.key ca.crt ca.srl wayne.key wayne.csr wayne.crt new_legit.p12 new_patched.p12
openssl genrsa -out ca.key 2048 >/dev/null 2>&1
openssl req -new -x509 -key ca.key -days 365 -out ca.crt -subj "/CN=santaclaus" >/dev/null 2>&1
openssl genrsa -out wayne.key 2048 >/dev/null 2>&1
openssl req -new -key wayne.key -out wayne.csr -subj "/CN=wayne" >/dev/null 2>&1
openssl x509 -req -in wayne.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out wayne.crt -days 365 >/dev/null 2>&1
openssl pkcs12 -export -inkey wayne.key -in wayne.crt -certfile ca.crt -name "wayne" -passout pass:pass -keypbe NONE -certpbe NONE -out new_legit.p12 >/dev/null 2>&1
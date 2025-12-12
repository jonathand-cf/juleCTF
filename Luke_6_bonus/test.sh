#!/usr/bin/env bash
set -euo pipefail

BASE="https://0ac760404670fe4a.julec.tf"
WORDLIST="/Users/jonathan/Documents/CTF/SecLists/Discovery/Web-Content/common.txt"

# vhost candidates
VHOSTS_FILE="$(mktemp)"
cat <<'EOF' > "$VHOSTS_FILE"
present
present-server
presentserver
presents
gifts
api-present
present_server
present-server.julec.tf
presentserver.julec.tf
EOF

echo "[+] Path fuzz (POST payload)"
ffuf -w "$WORDLIST" \
  -u "$BASE/FUZZ" \
  -X POST -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'presentname=flag&roles=santa' \
  -fs 150 -t 50 -of md -o path_hits.md

echo "[+] Vhost fuzz (Host header)"
ffuf -w "$VHOSTS_FILE" \
  -u "$BASE/" \
  -H "Host: FUZZ" \
  -fs 150 -t 50 -of md -o vhost_hits.md

echo "[+] Vhost fuzz (subdomain form)"
ffuf -w "$VHOSTS_FILE" \
  -u "$BASE/" \
  -H "Host: FUZZ.0ac760404670fe4a.julec.tf" \
  -fs 150 -t 50 -of md -o vhost_sub_hits.md

echo "[+] Done. Check path_hits.md / vhost_hits.md / vhost_sub_hits.md for any entries not size 150/404."

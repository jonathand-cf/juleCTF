#!/bin/bash

# Load environment variables from the .env file
if [ -f ".env" ]; then
    # shellcheck disable=SC1091
    source .env
else
    exit 1
fi

while true; do
  curl 'https://julec.tf/api/v1/plugins/ctfd-chall-manager/instance' \
    -X 'PATCH' \
    -H 'accept: application/json' \
    -H 'accept-language: en-GB,en;q=0.7' \
    -H 'cache-control: no-cache' \
    -H 'content-type: application/json' \
    -b "session=$SESSION" \
    -H "csrf-token:$CSRF_TOKEN" \
    -H 'origin: https://julec.tf' \
    -H 'pragma: no-cache' \
    -H 'priority: u=1, i' \
    -H 'referer: https://julec.tf/challenges' \
    -H 'sec-ch-ua: "Brave";v="143", "Chromium";v="143", "Not A(Brand";v="24"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "macOS"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'sec-gpc: 1' \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36' \
    --data-raw '{"challengeId":12}'

  echo "Curl command executed. Waiting 5 minutes..."
  sleep 300 # Wait for 300 seconds (5 minutes)
done
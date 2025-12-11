# JuleCTF – Luke 11

**Name:** timed_rsa  
**Author:** ciphr  
**Description:** We received RSA public keys with an encrypted message, but it seems we are receiving something more?

## Challenge

We are given an RSA service (via `ncat --ssl timed-rsa.julec.tf 1337`). The service prints the public key and ciphertext and, in DEBUG mode, leaks one of the primes in a funny `h`/`l` bitstring.

```bash
welcome to uber secure RSA services.
...
n=129044391092593358836413150444361449599586999672529961565676352574292420115748392669398411631596462334207482029115762256598167083787272273235753887121460000204841987429108754581244050136422971333516670803761495895794590247032120330844282728979335161028352231858221965500756138501790763250064894184931481083351
e=65537
ct=26475173276039843627709084403029130584817765758751327772557330551581345025072651271091414974772432261412987133577999917453363955648278471643948326901873147633545220698573650987989184280888860727616302931219207995314567671325830416277180499008620481681424487555385100213836758914694754525664097074976299260521
[DEBUG] verifying one of my primes
hhlhhhlllhhllhhhlhhlhhhhhhhhlhhhllhhlhhhllhhhhllhlhhhlhlhlhlllhlhllhllllhhllllhlhlhhlhhllhhlhlhhhhllhllhlhhhhhlllhhhlllhlhhllhhlhllhhhhlhllhhhhhlhlhhlllllhlhhlhllhllhllhhhhllhhlhhhhhhhhhlhllhhhllhlllhlhllllhllhlhhlhhllhhhlhhlllllllhhhhhlhhhlhlhllllllhlhlhhlhlhlhhhllhhlllhlhhlllllhlllhhlhhhhlhlhhhhlhhhlhhhhllhlllhlhhhlhlhhlhllhhlhhlhllllhhllhlhlllhhhhlhhlhllllhllhlhlhhhhlhhhlhlhhllllhllhhhhhhllhhhlllhhhlllhlhlhhhlhhhhlhlhlhlhlhllhlhhlllhlhllhhlhlhllllllhlhhhhlllhhhhhhllllhhhhhllhhlhlhhlhllhhlhllhhllllhlhhhlh
```

## Solution

1. Convert the leaked prime bits: `p = int(v.replace('h','1').replace('l','0'), 2)`.
2. Factor: `q = n // p` (it divides cleanly; both are 512-bit).
3. Compute `phi = (p-1)*(q-1)` and `d = pow(e, -1, phi)`.
4. Decrypt: `m = pow(ct, d, n)` then `m.to_bytes(...)` to get the plaintext.

Running solve.py prints the plaintext:

```txt
JUL{71m3_15_0f_3553nc3}
```

## Flag

`JUL{71m3_15_0f_3553nc3}`

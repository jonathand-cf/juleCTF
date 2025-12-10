# JuleCTF 2025

![JuleCTF banner](image.png)

Cyberlandslagsnissen trenger din hjelp! Hver dag i desember fram mot jul kommer det nye utfordringer innen cybersikkerhet.

Dette repositoryet inneholder utfordringer (tasks) og løsningsforslag for JuleCTF 2025.

## Table of Contents

- [Om](#om)
- [Oppgaver](#oppgaver)
- [Kjøring og testing](#kjøring-og-testing)
- [Repository-struktur](#repository-struktur)
- [Bidra](#bidra)
- [Lisens og kontakt](#lisens-og-kontakt)

## Om

Dette er en samling CTF-oppgaver og tilhørende writeups fra JuleCTF 2025. Oppgavene ligger i kataloger som `task2/`, `task3/`, osv. Hver oppgave-mappe inneholder nødvendige filer for reproduksjon og en `writeup.md` med forklaring.

## Oppgaver

- Se katalogene `task2`, `task3`, ..., `task9` for individuelle utfordringer.
- Hver oppgave-mappe har vanligvis en `writeup.md` som forklarer hvordan oppgaven ble løst.

## Kjøring og testing

- Mange oppgaver er kun statiske eller inneholder Python/JS-løsninger som kan kjøres direkte.
- Hvis en oppgave inneholder en `compose.yml` eller `Dockerfile`, kan du starte tjenester med Docker:

```bash
# fra repo-roten, gå til oppgave-mappen og start compose hvis tilstede
cd task6/santas_workshop || cd task6 || exit
docker compose up --build
```

- Kjør Python-skript direkte (anbefalt i en virtuell miljø):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # hvis fil finnes
python task8/exploit.py
```

Tilpass baner og kommandoer per oppgave; se `writeup.md` i hver mappe for detaljer.

## Repository-struktur

- `task*/` — Oppgavekataloger med koden og `writeup.md`.
- Noen oppgaver inneholder egne små web-apper eller Docker-oppsett under en `santas_workshop/` eller `bypass/`-mappe.

## Bidra

- Fork repoet, lag en feature branch, og åpne en pull request.
- For rapportering av feil eller spørsmål, bruk Issues i GitHub.

## Lisens og kontakt

- Ingen lisens er inkludert i dette repoet med mindre annet er oppgitt i en `LICENSE`-fil.
- For spørsmål, opprett en issue eller kontakt repo-eier via GitHub.

Lykke til — god jul og lykke til med CTF!

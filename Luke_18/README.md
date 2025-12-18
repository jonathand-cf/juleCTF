# Cyber Quest for Santa 3

**Author**: Shirajuki

**Descritpion**:
>Cyber, Cyber! Etter en lang reise gjennom portalen – forbi julevev, fengsel, blokker og kode i Minecraft, og endeløse looper i SoMe-strømmen – blir Cyber, Rudolf og reinsdyrene revet med av en voldsom datastrøm. Alle mister fotfestet og dras raskt mot kjernen av den digitale verdenen. Foran dem dukker en sverm av Santarobott-raketter opp. De låser seg på Cyber og skyter i vei, fast bestemt på å stoppe dem før målet. Midt i kaoset får Rudolf en merkelig følelse. Som om noen følger med. Noen kjent. Et blikk som ikke er fiendtlig – nesten oppmuntrende. Klarer du å navigere gjennom strømmen, unngå rakettene – og føre Cyber helt frem til målet?

**Link**: <https://cyber-quest-for-santa-3.julec.tf>

## Bot Automation Strategy

To obtain the ciphertext flag, we wrote a bot (`solve_bot.py`) to play the game automatically:

1. **WebSocket Connection**: Connects to the game server and initiates the game.
2. **Obstacle Tracking**: Maintains a queue of incoming obstacles (`spawn` messages).
3. **Pathfinding**: Calculates a target Y-position for each obstacle essentially by choosing a "safe margin" above or below the obstacle's Y-coordinate.
    - It evaluates `obstacle_y ± SAFE_MARGIN`.
    - It clamps the target to the field limits (`±200`).
    - It selects the target closest to the current position to minimize movement time.
4. **Movement Interpolation**: Smoothly updates the Y-position towards the target using a maximum speed approach to simulate game physics.
5. **Win Condition**: Upon surviving enough obstacles, the server sends a `win` message containing the `NSB{...}` ciphertext flag.

## Solution

The [solve_bot.py](solve_bot.py) got the ciphertext:
`NSB{cfp3e_esw0bok_4iw_e31iw33eq_e1w1iv_xk3_wtx4qxe34z}`
after getting score 111

### 1. Analysis

The prefix `NSB` shifts to `JUL` (the CTF theme).
We analyzed the ciphertext segments and mapped them to likely English words based on length and context:

- `cfp3e` -> `cyber`
- `esw0bok` -> `rudolph`
- `4iw` -> `and`
- `e31iw33eq` -> `reindeers`
- `e1w1iv` -> `riding`
- `xk3` -> `the`
- `wtx4qxe34z` -> `datastream`

### 2. Decryption & Leet Formatting

The cipher used a mix of Leet substitution (digits in ciphertext mapping to letters) and XOR/Shift for letters.
The recovered plaintext sentence is:
`cyber rudolph and reindeers riding the datastream`

Applying the standard Leet format observed in the challenge (`e`=3, `o`=0, `a`=4, `i`=1):

- `cyber` -> `cyb3r`
- `rudolph` -> `rud0lph`
- `and` -> `4nd`
- `reindeers` -> `r31nd33rs`
- `riding` -> `r1d1ng`
- `the` -> `th3`
- `datastream` -> `dat4str34m`

### Final Flag

`JUL{cyb3r_rud0lph_4nd_r31nd33rs_r1d1ng_th3_dat4str34m}`

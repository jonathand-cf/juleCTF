# Cyber Quest for Santa 1 — Writeup

- **Challenge:** Cyber Quest for Santa 1  
- **Authors:** Shirajuki, Tweey & olefredrik  
- **Link:** https://cyber-quest-for-santa-1.julec.tf  

## Description

> Cyber, Cyber, du må våkne!
>
> Cyberlandslagsnissen og reinsdyrene hans var på vei tilbake til Nordpolen for å gjøre klar julen da en mystisk digital virvel plutselig trakk dem inn i den digitale verdenen. Heldigvis klarte Rudolf akkurat å slippe unna.
>
> Nå trenger Rudolf din hjelp, Cyber! Som cybersikkerhetsekspert må du hjelpe å bryte inn i den digital verdenen og redde julen!

## Approach

1. Opened the site in Firefox and used **Override Content** on `index-DFzDK9Dl.js` to modify the client logic locally.
2. Disabled map collision bodies so the player could move “out of bounds”:
   - In `index-DFzDK9Dl.js`, replaced the collider creation block

     ```js
     if (collisions) {
       add rect/area/body for each collision object…
     }
     ```

     with a guard

     ```js
     if (!1 && collisions) { ... }
     ```

      effectively skipping collider creation.

      **Result**: player physics no longer registered the map walls, enabling free movement through the scene.
3. Reloaded with the overridden script and walked outside the intended play area to reach hidden NPC/reindeer locations without obstruction.
4. Each reindeer revealed a fragment of the flag; collecting and concatenating all parts produced the final flag.

## Flag
`JUL{l3ts_s4v3_4ll_th4m_r31nd33rs_4nd_m4yb3_4ls0_s4nta_f0r_th1s_chr1stm4s}`

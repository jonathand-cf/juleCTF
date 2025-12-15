#!/usr/bin/env python3
import curses
import time
from typing import Callable, Tuple

import requests
from requests.auth import HTTPBasicAuth

HOST = "http://129.241.150.69"
USERNAME = "admin"
PASSWORD = "a_long_password"
CHANNEL = 0
PULSE_SECONDS = 0.6  
TIMEOUT = 2.0


def _send(path: str) -> None:
    url = f"{HOST}/PSIA/YG/PTZCtrl/channels/{CHANNEL}/{path}"
    try:
        requests.put(url, auth=HTTPBasicAuth(USERNAME, PASSWORD), timeout=TIMEOUT)
    except Exception as exc:  # best-effort; don't crash on network hiccups
        print(f"[warn] request failed: {exc}")


def move(pan: int, tilt: int, seconds: float = PULSE_SECONDS) -> None:
    _send(f"continuous?pan={pan}&tilt={tilt}")
    time.sleep(seconds)
    _send("continuous?pan=0&tilt=0")


def zoom(direction: int, seconds: float = 0.4) -> None:
    # direction: 1 = in, -1 = out
    _send(f"continuous/zoom?data={direction}")
    time.sleep(seconds)
    _send("continuous/zoom?data=0")


def main(stdscr) -> None:
    stdscr.nodelay(True)
    curses.cbreak()
    stdscr.addstr(0, 0, "PTZ controller: arrows/WASD move, z=zoom in, x=zoom out, q=quit")
    stdscr.refresh()

    keymap: dict[int, Callable[[], None]] = {
        curses.KEY_UP: lambda: move(0, 1),
        curses.KEY_DOWN: lambda: move(0, -1),
        curses.KEY_LEFT: lambda: move(-1, 0),
        curses.KEY_RIGHT: lambda: move(1, 0),
        ord("w"): lambda: move(0, 1),
        ord("s"): lambda: move(0, -1),
        ord("a"): lambda: move(-1, 0),
        ord("d"): lambda: move(1, 0),
        ord("z"): lambda: zoom(1),
        ord("x"): lambda: zoom(-1),
    }

    while True:
        ch = stdscr.getch()
        if ch == -1:
            time.sleep(0.05)
            continue
        if ch in (ord("q"), ord("Q")):
            break
        action = keymap.get(ch)
        if action:
            action()


if __name__ == "__main__":
    curses.wrapper(main)

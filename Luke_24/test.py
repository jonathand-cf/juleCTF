#!/usr/bin/env python3
import asyncio, json, math, websockets

SPAWN = (972, 2671)
SWITCHES = [
    (1, (312, 1970)),
    (2, (1510, 1970)),
    (3, (1055, 1433)),
    (4, (1051, 939)),
]
EXTRA_TARGETS = [
    (1051, 750),
    (1051, 550),
    (1051, 320),
    (900, 200),
    (900, 120),
    (900, 40),
    (900, -40),
]

async def drain(ws, prefix=""):
    while True:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=0.005)
        except asyncio.TimeoutError:
            break
        else:
            try:
                data = json.loads(msg)
            except Exception:
                print(prefix, msg)
                continue
            if data.get("type") != "pos":
                print(prefix, msg)

async def walk(ws, start, target, step=40):
    x, y = start
    def step_to(x, y, tx, ty):
        dx, dy = tx - x, ty - y
        dist = math.hypot(dx, dy)
        if dist <= step:
            return tx, ty, True
        r = step / dist
        return x + dx * r, y + dy * r, False
    while True:
        x, y, done = step_to(x, y, *target)
        x, y = round(x), round(y)
        await ws.send(json.dumps({"type": "pos", "x": x, "y": y}))
        await drain(ws, prefix="> ")
        if done:
            break
    return (x, y)

async def main():
    async with websockets.connect("wss://cyber-quest-for-santa-4.julec.tf/server", ping_interval=None) as ws:
        print("spawn", await ws.recv())
        pos = SPAWN
        for sid, target in SWITCHES:
            pos = await walk(ws, pos, target)
            # a few extra position pings while on top of the switch
            for _ in range(3):
                await ws.send(json.dumps({"type": "pos", "x": target[0], "y": target[1]}))
            payload = {"type": "switch", "id": sid, "isAuthorized": True}
            if sid == 4:
                payload["superSecretBooleanFlag"] = True
            await ws.send(json.dumps(payload))
            try:
                for _ in range(6):
                    print("switch", sid, "resp", await asyncio.wait_for(ws.recv(), timeout=2))
            except asyncio.TimeoutError:
                pass
        # wander further north to see if door3 stays open and to catch any navigate message
        for target in EXTRA_TARGETS:
            pos = await walk(ws, pos, target)
            print("at", pos)
        # sweep across the map to try to hit the final trigger
        rows = [900, 800, 700, 600, 500, 400, 320, 200, 120]
        for y in rows:
            pos = await walk(ws, pos, (100, y))
            pos = await walk(ws, pos, (1900, y))
            pos = await walk(ws, pos, (100, y))
        # hang around for a bit to collect any remaining messages
        try:
            while True:
                print("final", await asyncio.wait_for(ws.recv(), timeout=5))
        except asyncio.TimeoutError:
            pass

asyncio.run(main())

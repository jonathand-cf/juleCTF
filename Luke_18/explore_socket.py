import asyncio
import websockets
import json
import time

URL = 'wss://cyber-quest-for-santa-3.julec.tf/server'
ORIGIN = 'https://cyber-quest-for-santa-3.julec.tf'

async def explore():
    print(f"Connecting to {URL}...")
    async with websockets.connect(URL, origin=ORIGIN) as websocket:
        print("Connected.")
        
        # Send start
        print("Sending {type: 'start'}...")
        await websocket.send(json.dumps({'type': 'start'}))
        
        # Try to cheat immediately
        print("Sending fake score...")
        await websocket.send(json.dumps({'type': 'score', 'passed': 112}))
        
        # Try cheat code
        print("Sending cheat code...")
        await websocket.send(json.dumps({'type': 'cheat', 'code': '111'}))

        last_heartbeat = time.time()
        
        try:
            while True:
                try:
                    msg = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                    print(f"[RECV] {msg}")
                    msg_json = json.loads(msg)
                    if msg_json.get('type') == 'win':
                        print(f"WIN: {msg_json}")
                        return
                    if msg_json.get('type') == 'gameover':
                        print(f"GAMEOVER: {msg_json}")
                        return
                except asyncio.TimeoutError:
                    pass
                
                # Send heartbeat
                if time.time() - last_heartbeat > 0.2:
                    hb = {'type': 'heartbeat', 'ts': int(time.time() * 1000), 'y': 0}
                    await websocket.send(json.dumps(hb))
                    last_heartbeat = time.time()
                    
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(explore())

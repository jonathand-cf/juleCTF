import asyncio
import websockets

URL = 'wss://cyber-quest-for-santa-3.julec.tf/server'
ORIGIN = 'https://cyber-quest-for-santa-3.julec.tf'

async def test():
    print(f"Connecting to {URL} with Origin: {ORIGIN}")
    try:
        async with websockets.connect(URL, origin=ORIGIN) as websocket:
            print("Connected!")
            msg = await websocket.recv()
            print(f"Received: {msg}")
            if msg == 'begin':
                await websocket.send('begin')
                print("Sent: begin")
                # Try a dummy pin
                await websocket.send('pass 000')
                print("Sent: pass 000")
                await websocket.send('key w967Tg15gB8NBtIOdzqeFw==')
                print("Sent: key ...")
                response = await websocket.recv()
                print(f"Response: {response}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test())

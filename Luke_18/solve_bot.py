import asyncio
import websockets
import json
import time
from collections import deque

URL = 'wss://cyber-quest-for-santa-3.julec.tf/server'
ORIGIN = 'https://cyber-quest-for-santa-3.julec.tf'

async def solve():
    print(f"Connecting to {URL}...")
    async with websockets.connect(URL, origin=ORIGIN) as websocket:
        print("Connected.")
        
        await websocket.send(json.dumps({'type': 'start'}))
        
        obstacle_queue = deque()
        current_y = 0.0
        target_y = 0.0
        
        last_heartbeat = time.time()
        # Initial speed test showed 800 was fine. Let's try 1000.
        MAX_SPEED = 1000.0
        SAFE_MARGIN = 130.0 # Increased margin
        FIELD_LIMIT = 200.0
        
        current_score = 0
        
        async def send_heartbeats():
            nonlocal current_y, target_y, last_heartbeat
            try:
                while True:
                    start_time = time.time()
                    
                    if obstacle_queue:
                        obstacle_y = float(obstacle_queue[0])
                        
                        # Calculate two potential safe spots
                        opt1 = obstacle_y + SAFE_MARGIN
                        opt2 = obstacle_y - SAFE_MARGIN
                        
                        # Filter validity
                        valid_opts = []
                        if -FIELD_LIMIT <= opt1 <= FIELD_LIMIT:
                            valid_opts.append(opt1)
                        if -FIELD_LIMIT <= opt2 <= FIELD_LIMIT:
                            valid_opts.append(opt2)
                            
                        # If no valid options (obstacle very large or weird pos), clamp to limits
                        if not valid_opts:
                            if obstacle_y > 0:
                                valid_opts.append(-FIELD_LIMIT)
                            else:
                                valid_opts.append(FIELD_LIMIT)
                        
                        # Pick closest to current_y
                        best_target = valid_opts[0]
                        min_dist = abs(best_target - current_y)
                        
                        for opt in valid_opts[1:]:
                            dist = abs(opt - current_y)
                            if dist < min_dist:
                                min_dist = dist
                                best_target = opt
                                
                        target_y = best_target
                    else:
                        target_y = 0.0
                    
                    # Interpolation
                    dt = time.time() - last_heartbeat
                    if dt > 0.1: dt = 0.05
                    
                    diff = target_y - current_y
                    step = MAX_SPEED * dt
                    
                    if abs(diff) <= step:
                        current_y = target_y
                    else:
                        current_y += step * (1 if diff > 0 else -1)
                        
                    last_heartbeat = time.time()
                    
                    try:
                        hb = {'type': 'heartbeat', 'ts': int(time.time() * 1000), 'y': current_y}
                        await websocket.send(json.dumps(hb))
                    except websockets.exceptions.ConnectionClosed:
                         break

                    elapsed = time.time() - start_time
                    await asyncio.sleep(max(0, 0.05 - elapsed))
                    
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Heartbeat error: {e}")

        heartbeat_task = asyncio.create_task(send_heartbeats())
        
        try:
            while True:
                msg = await websocket.recv()
                msg_json = json.loads(msg)
                msg_type = msg_json.get('type')
                
                if msg_type == 'spawn':
                    new_y = msg_json.get('y', 0)
                    obstacle_queue.append(new_y)
                    # print(f"Spawned: {new_y}. Queue: {len(obstacle_queue)}")
                    
                elif msg_type == 'score':
                    passed = msg_json.get('passed')
                    print(f"Score: {passed}")
                    current_score = passed
                    if obstacle_queue:
                        obstacle_queue.popleft()
                    
                elif msg_type == 'win':
                    print(f"WIN! Flag: {msg_json.get('flag')}")
                    return
                    
                elif msg_type == 'gameover':
                    print(f"GAMEOVER: {msg_json}")
                    print(f"State: CurY={current_y:.2f}, ObsY={obstacle_queue[0] if obstacle_queue else 'None'}, Target={target_y:.2f}")
                    return
                    
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"Error: {e}")
        finally:
            heartbeat_task.cancel()

if __name__ == "__main__":
    while True:
        try:
            asyncio.run(solve())
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Run exception: {e}")
        time.sleep(1)

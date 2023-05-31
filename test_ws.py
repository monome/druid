
import asyncio
import websockets

async def hello():
    uri = 'ws://localhost:6666'
    async with websockets.connect(uri) as websocket:
        while True:
            line = input('> ')
            if line.strip() == 'q':
                print('bye.')
                break
            await websocket.send(line)
            msg = await websocket.recv()
            print(msg)

asyncio.get_event_loop().run_until_complete(hello())

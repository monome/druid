import asyncio
import websockets
from websockets.exceptions import ConnectionClosedError


class DruidServer:

    def __init__(self, repl, host, port):
        self.repl = repl
        self.host = host
        self.port = port

    async def handle(self, websocket, path):
        (host, *args) = websocket.remote_address
        #self.repl.output(f'\n <ws connected: {host}>')
        self.repl.handlers['crow_output'].append(
            lambda output: asyncio.ensure_future(
                self.handle_output(websocket, output)
            )
        )
        try:
            async for message in websocket:
                self.repl.output(f'\n> {message}\n')
                self.repl.crow.writeline(message)
        except ConnectionClosedError as e:
            #self.repl.output(f'\n <ws disconnected: {host} ({e.code} {e.reason or "no reason"})>')
            pass
        else:
            #self.repl.output(f'\n <ws disconnected: {host}>')
            pass

    async def listen(self):
        self.repl.output(f' <listening at ws://{self.host}:{self.port}>')
        await websockets.serve(self.handle, self.host, self.port)

    async def handle_output(self, websocket, output):
        await websocket.send(output)

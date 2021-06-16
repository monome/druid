import asyncio
import websockets


class DruidServer:

    def __init__(self, repl, host, port):
        self.repl = repl
        self.host = host
        self.port = port

    async def handle(self, websocket, path):
        self.repl.handlers['crow_output'].append(
            lambda output: asyncio.ensure_future(
                self.handle_output(websocket, output)
            )
        )
        async for message in websocket:
            self.repl.output(f'\n> {message}\n')
            self.repl.crow.writeline(message)

    async def listen(self):
        self.repl.output(f' <listening at ws://{self.host}:{self.port}>')
        await websockets.serve(self.handle, self.host, self.port)

    async def handle_output(self, websocket, output):
        await websocket.send(output)

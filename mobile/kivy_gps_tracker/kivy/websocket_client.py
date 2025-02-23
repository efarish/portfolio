import ssl

import websockets


class WebSocketClient:
    def __init__(self, uri, jwt_header):
        self.uri = uri
        self.jwt_header = jwt_header
        self.websocket = None
        
    async def connect(self):
        if self.websocket is None or self.websocket.state != websockets.State.OPEN:
            print(f'Connecting with wss URI: {self.uri}')
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            self.websocket = await websockets.connect(uri=self.uri, ssl=ssl_context, 
                                                      additional_headers=self.jwt_header)
            print(f"Connected to {self.uri}")

    async def send(self, message):
        await self.connect()
        await self.websocket.send(message)

    async def receive(self):
        await self.connect()
        return await self.websocket.recv()

    async def close(self):
         if self.websocket:
            await self.websocket.close()
            self.websocket = None
            print("Disconnected")

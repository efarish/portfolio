import ssl

import certifi
import websockets


class WebSocketClient:
    def __init__(self, uri, jwt_header):
        self.uri = uri
        self.jwt_header = jwt_header
        self.websocket = None
        
    async def connect(self):
        if self.websocket is None: 
            print(f'Connecting with wss URI: {self.uri}')
            self.ssl_context = ssl.create_default_context(cafile=certifi.where())
            self.websocket = await websockets.connect(uri=self.uri, ssl=self.ssl_context, 
                                                      additional_headers=self.jwt_header)
            print(f"WebSocket connected to {self.uri}")

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

    async def close(self):
         if self.websocket:
            await self.websocket.close()
            self.websocket = None
            print("WebSocket Disconnected")


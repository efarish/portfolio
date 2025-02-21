"""
Client script that logs into remote app 
  and opens websocket.

Parameters:
  usr - user name to login in with.
  pwd - user password.
"""
import asyncio
import sys

import httpx
import websockets


class WebSocketClient:
    def __init__(self, uri, jwt_header):
        self.uri = uri
        self.jwt_header = jwt_header
        self.websocket = None
        
    async def connect(self):
        if self.websocket is None or self.websocket.state != websockets.State.OPEN:
            self.websocket = await websockets.connect(uri=self.uri, additional_headers=self.jwt_header)
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

async def main(ws_api, admin_headers):

    client = WebSocketClient(ws_api, admin_headers)
    await client.connect()

    await client.send("{'action':'updateLocation', 'user_name':'test_user', 'lat': 1.0, 'lng': 1.0}")
    response = await client.receive()
    print(f'Received: {response}')
    
    await client.send("{'action':'updateLocation', 'user_name':'test_user', 'lat': 2.0, 'lng': 2.0}")
    response2 = await client.receive()
    print(f'Received: {response2}')

    await client.close()
    

if __name__ == "__main__":

    rest_api = 'https://35gjbulhtk.execute-api.us-east-1.amazonaws.com'
    ws_api   = 'wss://8rbn146wuh.execute-api.us-east-1.amazonaws.com/production'

    print(f'{sys.argv=}')

    usr = sys.argv[1]
    pwd = sys.argv[2]

    response = httpx.post(rest_api + '/auth/token', data={"username": usr, 
                                                          "password": pwd, "grant_type": "password"},
                                                    headers={"content-type": "application/x-www-form-urlencoded"})
    print(f'{response.status_code}')
    admin_token = response.json()
    print(f'{admin_token=}')
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}", "Content-Type": "application/json"}
    print(f'{admin_headers=}')

    asyncio.run(main(ws_api, admin_headers))
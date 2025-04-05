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

CONFIG_API = 'https://<An HTTP accessible S3 folder >/config.json'

def get_config() -> dict:
    response = httpx.get(CONFIG_API)
    print(f'Config:{response.text}')
    props = response.json()['config'] 
    print(f'{props=}')
    return props

class WebSocketClient:
    def __init__(self, uri, jwt_header):
        self.uri = uri
        self.jwt_header = jwt_header
        self.websocket = None
        
    async def connect(self):
        if self.websocket is None or self.websocket.state != websockets.State.OPEN:
            print(f'{self.uri=}')
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

async def main(ws_api, admin_headers, usr):

    client = WebSocketClient(ws_api, admin_headers)

    await client.send(f'{{"action":"updateLocation", "user_name":"{usr}", "lat": 40.6743044, "lng": -73.9735552}}')
    print(f'Message sent.')
    
    while True:    
        response = await client.receive()
        print(f'Received: {response}')

    
if __name__ == "__main__":

    config = get_config()

    print(f'config=')

    rest_api = config['api'] 
    ws_api = config['ws_api'] 

    print(f'{sys.argv=}')

    usr = sys.argv[1]
    pwd = sys.argv[2]

    response = httpx.post(rest_api + 'auth/token', data={"username": usr, 
                                                          "password": pwd, "grant_type": "password"},
                                                    headers={"content-type": "application/x-www-form-urlencoded"})
    print(f'{response.status_code}')
    admin_token = response.json()
    print(f'{admin_token=}')
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}", "Content-Type": "application/json"}
    print(f'{admin_headers=}')

    asyncio.run(main(ws_api, admin_headers, usr))
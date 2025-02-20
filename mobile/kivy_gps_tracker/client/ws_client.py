import httpx
import websocket


def on_message(ws, message):
    print(f"Received message: {message}")

def on_error(ws, error):
    print(f"Encountered error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")
    print(f'{ws=}')
    print(f'{close_status_code=}')
    print(f'{close_msg=}')

def on_open(ws):
    print("Connection opened")
    #ws.send("Hello, Server!")
    ws.send("{'action':'updateLocation', 'user_name':'test_user', 'lat': 1.0, 'lng': 1.0}")

if __name__ == "__main__":

    api = 'https://ce0bls31xl.execute-api.us-east-1.amazonaws.com'

    response = httpx.post(api + '/auth/token', data={"username": "admin", 
                                                    "password": "a_password_", "grant_type": "password"},
                            headers={"content-type": "application/x-www-form-urlencoded"})
    print(f'{response.status_code}')
    admin_token = response.json()
    print(f'{admin_token=}')
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}", "Content-Type": "application/json"}
    print(f'{admin_headers=}')

    ws = websocket.WebSocketApp("wss://ifr5fwz8g6.execute-api.us-east-1.amazonaws.com/production",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close,
                                header=admin_headers)
    ws.on_open = on_open
    ws.run_forever()
    
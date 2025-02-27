import asyncio
import json

import httpx
from gpsblinker import GpsBlinker
from plyer import gps
from websocket_client import WebSocketClient

from kivy.app import App
from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivy.utils import platform

CONFIG_API = 'https://a-unique-public-bucket-name.s3.us-east-1.amazonaws.com/config.json'

def get_config() -> dict:
    """Method to download client app configuration."""
    response = httpx.get(CONFIG_API)
    print(f'Config:{response.text}')
    props = response.json()['config'] 
    print(f'{props=}')
    return props

async def location_updates(client):
    """Coroutine to receive location updates from WebSocket."""
    try:
        while True:
            print('Waiting for location updates....')
            position = await client.receive()
            print(f'Received a position update: {position=}')
            try:
                position = json.loads(position)
                if not 'action' in position and not 'user_name' in position:
                    print(f'Message not a position update: {position}')
                else:
                    App.get_running_app().update_blinker_positions([position,])
            except Exception as e:
                print(f'Location Update exception: {e}')
    except asyncio.CancelledError as ace:
        print(f'Location updates canceled: {ace}')
    except Exception as e:
        print(f'Location update exception: {e}')        
    finally:
        # when canceled, print that it finished
        print('Stopped location updates.')

async def send_location_update(client, user, lat, lng):
    """Coroutine to send GPS location to server using WebSocket."""
    try:
        print('Sending location update....')
        await client.send(f'{{"action":"updateLocation", "user_name": "{user}", "lat": {lat}, "lng": {lng}}}')
    except Exception as e:
        print('Sending update failed:', e)
    finally:
        # when canceled, print that it finished
        print('Done sending update.')

class Interface(ScreenManager):
    """
    The Kivy user interface. This class also managers location updates using: 
      1) The GPS service started by the Kivy app class and 
      2) Manages a WebSocket with the cloud service. 
    """
    btn_send = "Start Tracking..."
    btn_stop = "Stop Tracking"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.transition=FadeTransition()
        self.gps_blinker = None # Kivy Map Marker for application user. 
        self.token = None # JWT token of logged in user.
        self.user = None  # Application user name of logged in user.
        self.props = None # Application config retrieved from S3. 
        self.location_update_task = None # Coroutine for location updates.
        self.ws = None # A websocket connection.

    def switch_screen(self, screen_name: str):
        """
        Method used to switch between Kivy screens.
        """
        self.current = screen_name

    def sign_in(self):
        """
        Method used to log into application. A successful login results in 
        a JWT being returned to the user and will be used for all 
        subsequent requests.
        """
        user = self.ids.userIdTxt.text
        pwd = self.ids.passwordTxt.text
        self.props = get_config()

        if bool(self.props.get('debug', None)):
            self.token = '123'
            self.switch_screen('Map')
            return
        
        try:
            response = httpx.post(self.props['api'] + 'auth/token', 
                                data={"username": user, "password": pwd, "grant_type": "password"},
                                headers={"content-type": "application/x-www-form-urlencoded"})
            print(f'{response.status_code}')
            token = response.json()
            if response.status_code == 200:
                self.token = token['access_token']
                self.user = user
                print(f'{self.token=}')  
                self.switch_screen('Map')
            else:
                popup = Factory.ErrorPopup()
                popup.message.text = 'Login failed.'
                popup.open()
        except Exception as e:
            print(f'{e=}')
            popup = Factory.ErrorPopup()
            popup.message.text = 'Login failed.'
            popup.open()

    def register(self):
        """Create app users."""
        user = self.ids.userIdRegisterTxt.text
        pwd = self.ids.passwordRegisterTxt.text
        response = None
        if len(user.strip()) < 5 or len(pwd.strip()) <= 5:
            popup = Factory.ErrorPopup()
            popup.message.text = 'User name and passwords\n need to longer than 5 characters.'
            popup.open()
            return
        try:
            self.props = get_config()
            response = httpx.post(self.props['api'] + 'users/create_user', 
                                json={"user_name": user, "password": pwd, "role": "user"})
        except Exception as e:
            print(f'{e=}')
            popup = Factory.ErrorPopup()
            popup.message.text = 'Registration failed.'
            popup.open()
            return
        
        if response and response.status_code == 201:
            self.ids.userIdRegisterTxt.text = ""
            self.ids.passwordRegisterTxt.text = ""
            self.switch_screen('SignIn') 
        else: 
            popup = Factory.ErrorPopup()
            popup.message.text = response.json()['detail']
            popup.open()

    def on_map_relocated(self, **kwargs):
        pass
        
    async def start_updates(self):
        """Utility method to setup and initiate location updates."""
        # Start User marker. 
        if not self.gps_blinker:
            self.gps_blinker = self.ids.blinker
        self.gps_blinker.start()                
        #Start WebSocket.
        jwt_header = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        self.ws = WebSocketClient(self.props['ws_api'], jwt_header)
        await self.ws.connect()
        loop = App.get_running_app().event_loop
        self.location_update_task = loop.create_task(location_updates(self.ws))
        #Start User GPS updates.
        try:
            gps.start(5000, 10)
        except NotImplementedError:
            print(f'No GPS support on this platform.')         

    def stop_updates(self):
        """Utility method to stop and deallocate resources for location updates."""
        if self.gps_blinker: self.gps_blinker.stop()
        try:
          gps.stop()
        except NotImplementedError:
            print(f'No GPS support on this platform.')
        if self.location_update_task:
            self.location_update_task.cancel()
            self.location_update_task = None
        if self.ws: 
            loop = App.get_running_app().event_loop
            loop.create_task(self.ws.close())            
            self.ws = None

    def location_click(self):
        """Called by UI to start/stop location updates."""
        if self.ids.locationBtn.text == self.btn_send:
            try:
                self.ids.locationBtn.text = self.btn_stop
                loop.create_task(self.start_updates())
            except Exception as e:
                print(f'{e=}')
                popup = Factory.ErrorPopup()
                popup.message.text = 'Location tracking failed.'
                popup.open()
        else:
            self.stop_updates()
            self.ids.locationBtn.text = self.btn_send

    def signout_click(self):
        """Called by UI to logoff."""
        self.stop_updates()
        self.ids.locationBtn.text = self.btn_send
        App.get_running_app().close_gps_app()

class GpsTracker(App):
    """
    Kivy app class. This class also initializes the Kivy Garden GPS service.  
    """

    def __init__(self, event_loop, **kwargs):
        super().__init__(**kwargs)
        self.event_loop = event_loop
        self.lastMarker = None
        self.has_centered_map = False
        self.marker_map = {}
        self.lat = None
        self.lon = None

    def request_android_permissions(self):
        """
        Since API 23, Android requires permission to be requested at runtime.
        This function requests permission and handles the response via a
        callback.

        The request will produce a popup if permissions have not already been
        been granted, otherwise it will do nothing.
        """
        
        def callback(permissions, results):
            """
            Defines the callback to be fired when runtime permission
            has been granted or denied. This is not strictly required,
            but added for the sake of completeness.
            """
            if all([res for res in results]):
                print("callback. All permissions granted.")
            else:
                print("callback. Some permissions refused.")

        from android.permissions import Permission, request_permissions
        request_permissions([Permission.ACCESS_COARSE_LOCATION,
                             Permission.ACCESS_FINE_LOCATION], callback)

    def build(self):
        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
        except NotImplementedError:
            import traceback
            traceback.print_exc()
            self.gps_status = 'GPS is not implemented for your platform'

        if platform == "android":
            print("Android detected. Requesting permissions")
            self.request_android_permissions()
        else: print(f'Platform detected: {platform}')

    def on_start(self):
        print("App started.")

    def on_stop(self):
        print("App closed.")

    def on_location(self, **kwargs):
        gps_location = ' '.join([
            '{}={}'.format(k, v) for k, v in kwargs.items() if k in ['lat', 'lon', 'speed']])
        print(f'{gps_location=}')
        self.lon = kwargs['lon']
        self.lat = kwargs['lat']
        self.update_blinker_positions([])
        self.event_loop.create_task(send_location_update(self.root.ws, self.root.user, self.lat, self.lon))

    @mainthread
    def send_to_sign_in(self):
        self.root.switch_screen('SignIn')

    @mainthread
    def update_blinker_positions(self, positions):
        # First update the application user's marker.
        print(f'Updating blinker positions with: {positions}') 
        gps_blinker = self.root.ids.blinker
        if self.lat and self.lon:
            gps_blinker.lat = self.lat
            gps_blinker.lon = self.lon
        map = self.root.ids.theMap
        # Remove other user markers.
        for pos in positions:
            if pos['user_name'] == self.root.user:
                continue
            marker = self.marker_map.get(pos['user_name'], ...)
            if not marker is ...:
                print(f"Updating marker for {pos['user_name']}") 
                marker.lat = pos['lat']
                marker.lon = pos['lng']
            else:
                print(f"Adding new marker for {pos['user_name']}")
                m = GpsBlinker() 
                m.lat = pos['lat']
                m.lon = pos['lng']
                m.user_name = pos['user_name']
                self.marker_map[m.user_name] = m
                map.add_marker(m)
                m.start()            
        map.trigger_update(True)
        if not self.has_centered_map and self.lat and self.lon:
            map.center_on(self.lat, self.lon)
            self.has_centered_map = True

    @mainthread
    def on_status(self, stype, status):
        gps_status = 'stype={}, status={}'.format(stype, status)
        print(f'{gps_status=}')

    def close_gps_app(self):
        map = self.root.ids.theMap
        for marker in self.marker_map.values():
            marker.stop()
            map.remove_marker(marker)
        self.marker_map.clear()
        self.send_to_sign_in()

    def run_app(self):
        '''Run Kivy app.
        '''
        async def run_wrapper():
            await self.async_run(async_lib='asyncio')
            print('App done')

        return self.event_loop.create_task(run_wrapper())
                
if __name__ == '__main__':
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop) 
    loop.run_until_complete(GpsTracker(event_loop=loop).run_app())
    loop.close()

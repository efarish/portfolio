from threading import Thread

import httpx
from gpsblinker import GpsBlinker
from kivy_garden.mapview import MapMarker
from plyer import gps

from kivy.app import App
from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivy.utils import platform

CONFIG_API = 'https://a-unique-public-bucket-name.s3.us-east-1.amazonaws.com/config.json'
response = httpx.get(CONFIG_API)
print(f'Config:{response.text}')
API = response.json()['config']['api'] #TODO ENTER YOU API URL HERE!
print(f'{API=}')
DEBUG = False

class Interface(ScreenManager):

    btn_send = "Start Tracking..."
    btn_stop = "Stop Tracking"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.transition=FadeTransition()
        self.gps_blinker = None
        self.token = None

    def switch_screen(self, screen_name: str):
        self.current = screen_name

    def sign_in(self):
        user = self.ids.userIdTxt.text
        pwd = self.ids.passwordTxt.text

        if DEBUG:
            self.token = '123'
            self.switch_screen('Map')
            return

        try:
            response = httpx.post(API + '/auth/token', 
                                data={"username": user, "password": pwd, "grant_type": "password"},
                                headers={"content-type": "application/x-www-form-urlencoded"})
            print(f'{response.status_code}')
            token = response.json()
            if response.status_code == 200:
                self.token = token['access_token']
                print(f'{self.token=}')
                self.ids.userIdRegisterTxt.text = ""
                self.ids.passwordRegisterTxt.text = ""                
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
        user = self.ids.userIdRegisterTxt.text
        pwd = self.ids.passwordRegisterTxt.text
        response = None
        if len(user.strip()) < 5 or len(pwd.strip()) <= 5:
            popup = Factory.ErrorPopup()
            popup.message.text = 'User name and passwords\n need to longer than 5 characters.'
            popup.open()
            return
        try:
            response = httpx.post(API + '/users/create_user', 
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
        
    def location_click(self):
        if self.ids.locationBtn.text == self.btn_send:
            try:
                if not self.gps_blinker:
                    self.gps_blinker = self.ids.blinker
                    self.gps_blinker.blink()                
                gps.start(5000, 10)
                self.ids.locationBtn.text = self.btn_stop                
            except Exception as e:
                print(f'{e=}')
                popup = Factory.ErrorPopup()
                popup.message.text = 'Location tracking failed.'
                popup.open()
        else:
            self.ids.locationBtn.text = self.btn_send
            gps.stop()

def worker(gpsTracker):
    print('Worker started')
    token = gpsTracker.root.token
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = httpx.post(API + '/location/update', 
                             json={'user_name': 'user1', 'lat': gpsTracker.lat, 'lng': gpsTracker.lon},
                             headers=headers)
    positions = []
    if response.status_code == 201:
        positions = response.json()
        gpsTracker.update_blinker_positions(positions)
    elif response.status_code in [401, 403]: # Forbidden: probably a sign-in expiration.
        gpsTracker.send_to_sign_in()
    else:
        print(f'Location update failed: {response.status_code=} {response.text=}')

class GpsTracker(App):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.lastMarker = None
        self.has_centered_map = False

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
        else: print(f'Not a supported platform: {platform}')

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
        p = Thread(target=worker, args=(self,))
        p.start()

    @mainthread
    def send_to_sign_in(self):
        self.root.switch_screen('SignIn')

    @mainthread
    def update_blinker_positions(self, positions):
        print('Blinker update positions..')
        print(f'{positions=}')
        gps_blinker = self.root.ids.blinker
        gps_blinker.lat = self.lat
        gps_blinker.lon = self.lon
        map = self.root.ids.theMap
        map.trigger_update(True)
        if not self.has_centered_map:
            map.center_on(self.lat, self.lon)
            self.has_centered_map = True

    @mainthread
    def on_status(self, stype, status):
        gps_status = 'stype={}, status={}'.format(stype, status)
        print(f'{gps_status=}')

if __name__ == '__main__':
    
    GpsTracker().run()

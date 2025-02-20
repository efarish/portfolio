from os.path import dirname, join
from threading import Thread

import httpx
from gpsblinker import GpsBlinker
from plyer import gps

from kivy.app import App
from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivy.utils import platform

CONFIG_API = 'https://a-unique-public-bucket-name.s3.us-east-1.amazonaws.com/config.json'

def get_config() -> dict:
    response = httpx.get(CONFIG_API)
    print(f'Config:{response.text}')
    props = response.json()['config'] 
    print(f'{props=}')
    return props

class Interface(ScreenManager):
    """
    The Kivy user interface. 
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

    def switch_screen(self, screen_name: str):
        """
        Method used to swtich between Kivy screens.
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
            response = httpx.post(self.props['api'] + '/auth/token', 
                                data={"username": user, "password": pwd, "grant_type": "password"},
                                headers={"content-type": "application/x-www-form-urlencoded"})
            print(f'{response.status_code}')
            token = response.json()
            if response.status_code == 200:
                self.token = token['access_token']
                self.user = user
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
            self.props = get_config()
            response = httpx.post(self.props['api'] + '/users/create_user', 
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
                self.gps_blinker.start()                
                gps.start(5000, 10)
                self.ids.locationBtn.text = self.btn_stop                
            except Exception as e:
                print(f'{e=}')
                popup = Factory.ErrorPopup()
                popup.message.text = 'Location tracking failed.'
                popup.open()
        else:
            self.ids.locationBtn.text = self.btn_send
            self.gps_blinker.stop()
            gps.stop()

    def signout_click(self):
        if gps: gps.stop
        if self.gps_blinker: self.gps_blinker.stop()
        self.ids.locationBtn.text = self.btn_send
        App.get_running_app().close_gps_app()


def worker(gpsTracker):
    """
    Function to be called by worker Thread report application user's 
      GPS position. The endpoint used to report the user GPS position
      also returns the position of anyone else logged into the application.
    """
    print('Worker started')
    token = gpsTracker.root.token
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    api = gpsTracker.root.props['api']

    response = None
    try:
        response = httpx.post(api + '/location/update', 
                                json={'user_name': 'user1', 'lat': gpsTracker.lat, 'lng': gpsTracker.lon},
                                headers=headers)
    except Exception as e:
        print(f'Error occurred while sending location: {e}')

    if response is None:
        gpsTracker.update_blinker_positions([])
    elif response.status_code == 201:
        # Reporting of user's GPS position was successful.
        #  The response will contain the GPS position of all other 
        #  users logged into the application. 
        positions = response.json()
        gpsTracker.update_blinker_positions(positions)
    elif response.status_code in [401, 403]: 
        # Forbidden: probably a sign-in expiration.
        #  Return user to login screen.
        gpsTracker.root.signout_click()
    else:
        print(f'Location update failed: {response.status_code=} {response.text=}')

class GpsTracker(App):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.lastMarker = None
        self.has_centered_map = False
        self.marker_list = []

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
        if self.root.props['debug']:
          self.update_blinker_positions([])
        else:
          p = Thread(target=worker, args=(self,))
          p.start()

    @mainthread
    def send_to_sign_in(self):
        self.root.switch_screen('SignIn')

    @mainthread
    def update_blinker_positions(self, positions):
        # First update the application user's marker. 
        gps_blinker = self.root.ids.blinker
        gps_blinker.lat = self.lat
        gps_blinker.lon = self.lon
        map = self.root.ids.theMap
        # Remove other users markers.
        for marker in self.marker_list:
            marker.stop()
            map.remove_marker(marker)
        self.marker_list.clear()
        # Add markers for any users found by the endpoint.
        for pos in positions: 
            if pos['user_name'] != self.root.user:
                m = GpsBlinker() 
                m.lat = pos['lat']
                m.lon = pos['lng']
                self.marker_list.append(m)
                map.add_marker(m)
                m.start()
        map.trigger_update(True)
        if not self.has_centered_map:
            map.center_on(self.lat, self.lon)
            self.has_centered_map = True

    @mainthread
    def on_status(self, stype, status):
        gps_status = 'stype={}, status={}'.format(stype, status)
        print(f'{gps_status=}')

    def close_gps_app(self):
        map = self.root.ids.theMap
        for marker in self.marker_list:
            marker.stop()
            map.remove_marker(marker)
        self.marker_list.clear()
        self.send_to_sign_in()
                
if __name__ == '__main__':
    
    GpsTracker().run()

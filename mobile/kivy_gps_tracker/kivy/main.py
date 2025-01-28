import httpx
from layouts.BgBoxLayout import BgBoxLayout
from plyer import gps

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.factory import Factory
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.uix.screenmanager import FadeTransition, ScreenManager
from kivy.utils import platform

API = 'https://u67pk2go93.execute-api.us-east-1.amazonaws.com' #TODO ENTER YOU API URL HERE!

class Interface(ScreenManager):

    btn_send = "Start Tracking..."
    btn_stop = "Stop Tracking"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.transition=FadeTransition()

    def switch_screen(self, screen_name: str):
        self.current = screen_name

    def sign_in(self):
        user = self.ids.userIdTxt.text
        pwd = self.ids.passwordTxt.text
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

    def location_click(self):
        if self.ids.locationBtn.text == self.btn_send:
            try:
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
            

class GpsTracker(App):

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

    @mainthread
    def on_location(self, **kwargs):
        gps_location = ' '.join([
            '{}={}'.format(k, v) for k, v in kwargs.items() if k in ['lat', 'lon', 'speed']])
        print(f'{gps_location=}')
        lbl=Label(text=gps_location, size_hint=(None,None), size=(dp(300),dp(50)), halign='left')
        self.root.ids.boxLayout.add_widget(lbl, len(self.root.ids.boxLayout.children))

    @mainthread
    def on_status(self, stype, status):
        gps_status = 'stype={}, status={}'.format(stype, status)
        print(f'{gps_status=}')

if __name__ == '__main__':
    
    GpsTracker().run()

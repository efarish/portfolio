from layouts.BgBoxLayout import BgBoxLayout
from plyer import gps

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.metrics import dp
from kivy.uix.label import Label
from kivy.utils import platform


class Interface(BgBoxLayout):

    btn_send = "Start Tracking..."
    btn_stop = "Stop Tracking"

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        
    def clear(self):
        self.ids.stackLayout.clear_widgets()

    def location_click(self):
        if self.ids.locationBtn.text == self.btn_send:
            self.ids.locationBtn.text = self.btn_stop
            gps.start(1000, 0)

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
        from android.permissions import Permission, request_permissions

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
        else: print(f'Unexpected platform: {platform}')

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

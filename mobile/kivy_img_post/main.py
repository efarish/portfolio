import time
from queue import Queue

#Multiprocessing.Queue is not supported on Android per https://bugs.python.org/issue3770.
#  Therefore, the queue and threading packages where used.
#from multiprocessing import Process, Queue 
from threading import Thread as Process

import requests
from android.permissions import Permission, request_permissions
from android.storage import (
    primary_external_storage_path,
    secondary_external_storage_path,
)
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

URL = ' TODO ' #SET ENDPOINT URL HERE!!!!! 

Builder.load_file('./kivy.kv')

def worker(q, img_file):
    """
    Method called by worker thread, The thread is started by clicking on 
      window Capture button of the CameraClick class below. The URL endpoint is 
      called and the response put on the queue.       
    """
    try:
        with open(img_file, 'rb') as image_file:
                response = requests.post(URL, data=image_file)
        if response.status_code == 200:
            response_msg = response.text
        else:
            response_msg = f"Error uploading image: {response.status_code}, {response.text}" 
        print(response_msg)    
        print(f'{response.status_code=}')
        print(f'{response.text=}') 
        q.put(response_msg)
    except Exception as ex:
        q.put(str(ex))

class CameraClick(BoxLayout):

    def __init__(self, mp_app, **kwargs):
        super().__init__(**kwargs)
        self.app = mp_app

    def capture(self):
        """
        This function to captures the images using the device's 
          camera. The file is stored in the download directory and 
           given the name IMG_YMD_HMS.
        """
        primary_ext_storage = primary_external_storage_path()
        secondary_ext_storage = secondary_external_storage_path()
        print("Primary Storage:", primary_ext_storage)
        print("Secondary Storage:", secondary_ext_storage)
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        img_file = "/storage/emulated/0/Download/IMG_{}.png".format(timestr)
        camera.export_to_png(img_file)
        p = Process(target=worker, args=(self.app.q, img_file,))
        p.start()
        print("Captured") 
        
class TestCamera(App):

    def build(self):
        # Create the queue that is shared between the 
        #  TestCamera app and the worker threads.
        self.q = Queue()
        # Create Kivy callback timer to check the queue.
        Clock.schedule_interval(self.show_response, 2)
        request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
        ])
        return CameraClick(mp_app=self)
                            
    def show_popup(self, data):
        popup = Factory.ErrorPopup()
        popup.message.text = data
        popup.open()

    def show_response(self, dt):
        if not self.q.empty():
            data = self.q.get()        
            self.show_popup(data)

    def on_stop(self):
        print("App closed.")


if __name__ == '__main__':
    
    TestCamera().run()

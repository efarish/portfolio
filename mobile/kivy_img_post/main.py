'''
Camera Example
==============

This example demonstrates a simple use of the camera. It shows a window with
a buttoned labelled 'play' to turn the camera on and off. Note that
not finding a camera, perhaps because gstreamer is not installed, will
throw an exception during the kv language processing.

'''

# Uncomment these lines to see all the messages
# from kivy.logger import Logger
# import logging
# Logger.setLevel(logging.TRACE)

import requests

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time
from android.permissions import request_permissions, Permission
from android.storage import primary_external_storage_path, secondary_external_storage_path

URL = 'TODO' #SET ENDPOINT URL HERE!!!!! 

Builder.load_string('''
<CameraClick>:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: False
        allow_stretch: True
        canvas.before:
            PushMatrix
            Rotate:
                angle: -90
                origin: self.center
        canvas.after:
            PopMatrix
    ToggleButton:
        text: 'Play'
        on_press: camera.play = not camera.play
        size_hint_y: None
        height: '48dp'
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_press: root.capture()
''')


class CameraClick(BoxLayout):
    def capture(self):
        '''
        Function to capture the images and give them the names
        according to their captured time and date.
        '''
        primary_ext_storage = primary_external_storage_path()
        secondary_ext_storage = secondary_external_storage_path()
        print("Primary Storage:", primary_ext_storage)
        print("Secondary Storage:", secondary_ext_storage)
        camera = self.ids['camera']
        timestr = time.strftime("%Y%m%d_%H%M%S")
        img_file = "/storage/emulated/0/Download/IMG_{}.png".format(timestr)
        camera.export_to_png(img_file)
        with open(img_file, 'rb') as image_file:
             response = requests.post(URL, data=image_file)
        if response.status_code == 200:
            print("Image uploaded successfully!")
        else:
            print("Error uploading image:", response.status_code)
        print(f'{response.status_code=}')
        print(f'{response.text=}')   
        print("Captured")


class TestCamera(App):

    def build(self):
        request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
        ])
        return CameraClick()


TestCamera().run()

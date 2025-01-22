
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.properties import BoundedNumericProperty, StringProperty
from kivy.uix.stacklayout import StackLayout


class BgStackLayout(StackLayout):
    alpha=BoundedNumericProperty(0, min=0, max=1)
    hex_code=StringProperty("#FFFFFF")
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.create_background)
        Clock.schedule_interval(self.update,1/30)
    def hex_to_rgb(self,hex):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex[i:i + 2], 16)
            rgb.append(decimal/255)
        return rgb
    def update(self, *args):
        self.rect.pos=self.pos
        self.rect.size=self.size
    def create_background(self, *args):
        self.hex_code=str(self.hex_code).split("#")[-1]
        r,g,b=self.hex_to_rgb(self.hex_code)
        with self.canvas.before:
            Color(r,g,b,self.alpha)
            self.rect=Rectangle(pos=self.pos, size=self.size)
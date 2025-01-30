from kivy_garden.mapview import MapMarker

from kivy.animation import Animation


class GpsBlinker(MapMarker):
    def __init__(self, **kwargs):
        super(GpsBlinker, self).__init__(**kwargs)

    def blink(self):
        anim = Animation(opacity=0, blink_size=0)
        anim.bind(on_complete=self.reset)
        anim.start(self)


    def reset(self, *args):
        self.opacity = 1
        self.blink_size = self.default_blink_size
        self.blink()
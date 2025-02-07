from kivy_garden.mapview import MapMarker

from kivy.animation import Animation


class GpsBlinker(MapMarker):
    def __init__(self, **kwargs):
        super(GpsBlinker, self).__init__(**kwargs)
        self._stop = True
        self._debug = False

    def _blink(self):
        anim = Animation(opacity=0, blink_size=0)
        anim.bind(on_complete=self.reset)
        anim.start(self)

    def reset(self, *args):
        if self._stop: return
        self.opacity = 1
        self.blink_size = self.default_blink_size
        self._blink()
    
    def stop(self):
        self._stop = True

    def start(self):
        if self._stop:
            self._stop = False
            self._blink()

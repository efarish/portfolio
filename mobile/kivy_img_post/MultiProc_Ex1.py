from datetime import datetime
from multiprocessing import Process, Queue

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

"""
Configure Kivy GUI. This configuration connnects 
  the GUI class method LaunchProc.launch.
"""
Builder.load_string('''
<LaunchProc>:
    orientation: "vertical"
    Label:
        id: my_label
        text: "Hello, Proc!"
    Button:
        text: 'Launch'
        size_hint_y: None
        height: '48dp'
        on_press: root.launch()
''')

def worker(q):
    """
    Method called by worker threads started by clicking on 
      GUI's Launch button.  
    """
    print('Worker running...')
    q.put(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print('Worker ran.')

class LaunchProc(BoxLayout):
    """
    Kivy GUI that launches worker thread.
    """

    def __init__(self, mp_app, **kwargs):
        super().__init__(**kwargs)
        self.app = mp_app

    def launch(self):
        print('Launch started...')
        p = Process(target=worker, args=(self.app.q,))
        p.start()
        print('Launch finished.')

class TestProc(App):
    """
    Kivy application that creates the GUI and
      updates it when called by worker threads.
    """

    def build(self):
        self.q = Queue()
        Clock.schedule_interval(self.update_label, 2)
        return LaunchProc(mp_app=self)
    
    def update_label(self, dt):
        if not self.q.empty():
            while not self.q.empty():
                data = self.q.get()
                self.root.ids.my_label.text = f"Now: {data}"

    def on_stop(self):
        print("App closed.")


if __name__ == '__main__':
    TestProc().run()

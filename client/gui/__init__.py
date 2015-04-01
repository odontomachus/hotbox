import tkinter as tk

from client import Client
from .controls import Controls
from .display import Display

class Logger(tk.Frame):
    def error(self, message):
        pass
    def warn(self, message):
        pass
    def log(self, message):
        pass

class Config(tk.Frame):
    def __init__(self, controller, *args, **kwargs):
        self.controller = controller
        super().__init__(*args, **kwargs)
        self.port='COM4'
        # @TODO port
        # output file
        # temp 30 - 145
        # time 0 - 3600*9
        self.save = tk.Button(self, text="Save", command = self.configure)

    def configure(self):
        controller.configure(self.time, self. temp)

class App:
    def __init__(self):
        # Open main window
        root = tk.Tk()
        root.title("Hotbox")
        root.wm_geometry('800x600')
        self.root = root

        self.logger = Logger()
        self.display = Display(self.logger)

        # setup client
        self.controller = Client()
        self.controller.register(('status',), self.state_change)
        self.controller.register(('run_status',), self.display.run_message)

        self.config = Config(self.controller)

        # connect client
        self.controller.connect(self.config.port)

        self.controls = Controls(self.controller)
        self.controls.grid()


    def state_change(self, state):
        self.controls.state_change(state)
        self.log.state_change(state)

    def configure(self):
        """ Show configuration panel """
        pass

    def run(self):
        """ Show run info panel """
        self.status_frame = sf = tk.Frame(self.root)

        

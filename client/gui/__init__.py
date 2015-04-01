import tkinter as tk

from client import Client
from .controls import Controls
from .display import Display
from .config import Config, ConfigPort

class Logger(tk.Frame):
    def error(self, message):
        pass
    def warn(self, message):
        pass
    def log(self, message):
        pass

class App:
    def __init__(self):
        # Open main window
        root = tk.Tk()
        root.title("Hotbox")
        root.wm_geometry('800x600')
        self.root = root

        self.menu = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Set Port', command=self.configure_port)
        self.file_menu.add_command(label='Configure', command=self.configure)
        self.file_menu.add_command(label='Quit', command=root.quit)
        root['menu'] = self.menu

        self.logger = Logger()
        self.display = Display(self.logger)

        # setup client
        self.controller = Client()
        self.config_port = ConfigPort(self.main, self.controller)
        self.config = Config(self.main, self.controller)

        self.controller.register(('status',), self.state_change)
        self.controller.register(('run_status',), self.display.run_message)
        self.controller.register(('config',), self.config.update_config)

        # connect client
        self.controller.connect(self.config_port.port)

        self.controls = Controls(self.controller)
        self.controls.grid()


    def state_change(self, state):
        self.controls.state_change(state)
        self.log.state_change(state)

    def configure(self):
        """ Show configuration panel """
        self.controls.grid_forget()
        self.display.grid_forget()
        self.config_port.grid_forget()
        self.config.grid()

    def configure_port(self):
        self.controls.grid_forget()
        self.display.grid_forget()
        self.config_port.grid()
        self.config.grid_forget()

    def main(self):
        self.config.grid_forget()
        self.config_port.grid_forget()
        self.controls.grid()
        self.display.grid()

        

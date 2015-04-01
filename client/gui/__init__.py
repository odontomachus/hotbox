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
    def __init__(self, done, controller, *args, **kwargs):
        """ Configuration panel and actions.

        @param done: callback to run when finished configurationt task.
        @param controller: serial client to send configuration to.
        """

        self.done = done
        self.controller = controller
        super().__init__(*args, **kwargs)

        self.v_port = tk.StringVar()
        self.v_temp = tk.IntVar()
        self.v_time = tk.IntVar()

        self.port = 'COM4'
        self.time = 6*3600
        self.temp = 53
        self.v_port.set(self.port)
        self.v_time.set(self.time)
        self.v_temp.set(self.temp)

        tk.Label(self, text="Serial Port").grid(column=0, row=0)
        tk.Entry(self, exportselection=0, textvariable=self.v_port).grid(column=1, row=0)

        tk.Label(self, text="Heating Temperature").grid(column=0, row=1)
        tk.Entry(self, exportselection=0, textvariable=self.v_temp).grid(column=1, row=1)

        tk.Label(self, text="Heating Time").grid(column=0, row=2)
        tk.Entry(self, exportselection=0, textvariable=self.v_time).grid(column=1, row=2)

        tk.Button(self, text="Cancel", command = self.done).grid(column=0,row=3)
        tk.Button(self, text="Save", command = self.configure).grid(column=1,row=3)

    def configure(self):
        self.port = self.v_port.get()
        self.time = self.v_time.get()
        self.temp = self.v_temp.get()
        controller.configure(self.time, self.temp)
        self.done()

    def update_config(self, config):
        self.time = config.time
        self.temp = config.temp

class App:
    def __init__(self):
        # Open main window
        root = tk.Tk()
        root.title("Hotbox")
        root.wm_geometry('800x600')
        self.root = root

        self.menu = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Configure', command=self.configure)
        root['menu'] = self.menu

        self.logger = Logger()
        self.display = Display(self.logger)

        # setup client
        self.controller = Client()
        self.config = Config(self.main, self.controller)

        self.controller.register(('status',), self.state_change)
        self.controller.register(('run_status',), self.display.run_message)
        self.controller.register(('config',), self.config.update_config)

        # connect client
        self.controller.connect(self.config.port)

        self.controls = Controls(self.controller)
        self.controls.grid()


    def state_change(self, state):
        self.controls.state_change(state)
        self.log.state_change(state)

    def configure(self):
        """ Show configuration panel """
        self.controls.grid_forget()
        self.display.grid_forget()
        self.config.grid()

    def main(self):
        self.config.grid_forget()
        self.controls.grid()
        self.display.grid()

        

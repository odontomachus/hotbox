import threading
import tkinter as tk
import queue

from time import sleep

import client
from .controls import Controls
from .display import Display
from .config import Config, ConfigPort

class Logger(tk.Frame):
    def error(self, message):
        print(message)
    def warn(self, message):
        print(message)
    def log(self, message):
        print(message)

class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        # Open main window
        self.master.title("Hotbox")
        self.master.wm_geometry('650x693')

        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='Set Port', command=self.configure_port)
        file_menu.add_command(label='Configure', command=self.configure)
        file_menu.add_command(label='Controls', command=self.main)
        file_menu.add_command(label='Quit', command=self.quit)
        self.master['menu'] = menu

        self.logger = Logger()
        self.display = Display(self.logger)

        # setup client
        self.controller = client.Client()
        self.config_port = ConfigPort(self.main, self.controller)
        self.config = Config(self.main, self.controller)

        self.controls = Controls(self.controller)
        self.controls.grid()
        self.display.grid()

        # connect client
        self.controller.start()
        self.controller.connect(self.config_port.port)

        # callbacks for event response
        self.callbacks = (
            (self.controller.msg_queue[client.MSG_RUN_STATUS], 
             self.display.run_message),
            (self.controller.msg_queue[client.MSG_CONFIG],
             self.config.update_config),
            (self.controller.msg_queue[client.MSG_STATUS],
             self.state_change),
        )

        # start serial event polling
        self.poll()

    def state_change(self, message):
        self.controls.state_change(message.status)
        self.display.state_change(message.status)

    def quit(self):
        # stop serial client thread
        self.controller.running = False
        super().quit()

    def destroy(self):
        # stop serial client thread
        self.controller.running = False
        super().destroy()

    def configure(self):
        """ Show configuration panel """
        self.controller.oven_query_config()
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

    def poll(self):
        for (mqueue, callback) in self.callbacks:
            try:
                message = mqueue.get_nowait()
                if message:
                    callback(message)
            except queue.Empty:
                pass

        self.master.after(100, self.poll)



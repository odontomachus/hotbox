from collections import OrderedDict
import tkinter as tk

import client

class StartButton(tk.Button):
    def state_change(self, status):
        if status == client.STATE_READY:
            self['state'] = tk.NORMAL
        else:
            self['state'] = tk.DISABLED

class StopButton(tk.Button):
    def state_change(self, status):
        if status == client.STATE_ACTIVE:
            self['state'] = tk.NORMAL
        else:
            self['state'] = tk.DISABLED

class Controls(tk.Frame):
    def __init__(self, controller, *args, **kwargs):
        if ('pady' not in kwargs):
            kwargs['pady'] = 10
        super().__init__(*args, **kwargs)
        self.buttons = buttons = OrderedDict()
        buttons['start'] = StartButton(self, text='Start', command = controller.oven_start, state=tk.DISABLED)
        buttons['stop'] = StopButton(self, text='Stop', command = controller.oven_stop, state=tk.DISABLED)
        for (col, button) in enumerate(buttons.values()):
            button.grid(column=col, row=0)

    def state_change(self, status):
        for button in self.buttons.values():
            button.state_change(status)


from collections import OrderedDict
import tkinter as tk

class StartButton(tk.Button):
    def update(self, state):
        if state in ['running', 'disconnected']:
            self['state'] = tx.DISABLED

class StopButton(tk.Button):
    def update(self, state):
        if state in ['running', 'disconnected']:
            self['state'] = tx.NORMAL

class Controls(tk.Frame):
    def __init__(self, controller, *args, **kwargs):
        self.controller = controller
        super().__init__(*args, **kwargs)
        self.buttons = buttons = OrderedDict()
        buttons['start'] = StartButton(self, text='Start', command = controller.start)
        buttons['stop'] = StopButton(self, text='Stop', command = controller.stop)
        for (col, button) in enumerate(self.buttons.values()):
            button.grid(column=col, row=0)

    def state_change(self, state):
        for button in self.buttons.values():
            button.update(state)


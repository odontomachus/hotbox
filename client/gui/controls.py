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

        self.dash_frame = tk.Frame(self, pady=10)
        tk.Label(self.dash_frame, text="Serial connection status:").pack()
        self.connected_dash = tk.Canvas(self.dash_frame, width=81, height=50)
        self.connected_dash.pack()
        self.dash_frame.grid(columnspan=2)
        self.connected_img = tk.PhotoImage(file='data/img/connected.gif')
        self.disconnected_img = tk.PhotoImage(file='data/img/disconnected.gif')
        self.img_id = self.connected_dash.create_image(1, 1, anchor='nw',
                        image=self.connected_img,
                        disabledimage=self.disconnected_img,
                        state=tk.DISABLED)


        self.buttons = buttons = OrderedDict()
        buttons['start'] = StartButton(self, text='Start', command = controller.oven_start, state=tk.DISABLED)
        buttons['stop'] = StopButton(self, text='Stop', command = controller.oven_stop, state=tk.DISABLED)
        for (col, button) in enumerate(buttons.values()):
            button.grid(column=col, row=1)

    def state_change(self, status):
        for button in self.buttons.values():
            button.state_change(status)
        if status == client.STATE_DISCONNECTED:
            self.connected_dash.itemconfigure(self.img_id, state=tk.DISABLED)
        else:
            self.connected_dash.itemconfigure(self.img_id, state=tk.NORMAL)

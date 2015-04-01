import tkinter as tk

class Config(tk.Frame):
    def __init__(self, done, controller, *args, **kwargs):
        """ Configuration panel and actions.

        @param done: callback to run when finished configurationt task.
        @param controller: serial client to send configuration to.
        """

        self.done = done
        self.controller = controller
        super().__init__(*args, **kwargs)

        self.v_temp = tk.IntVar()
        self.v_time = tk.IntVar()

        self.time = 6*3600
        self.temp = 53
        self.v_time.set(self.time)
        self.v_temp.set(self.temp)

        tk.Label(self, text="Heating Temperature").grid(column=0, row=0)
        tk.Entry(self, exportselection=0, textvariable=self.v_temp).grid(column=1, row=0)

        tk.Label(self, text="Heating Time").grid(column=0, row=1)
        tk.Entry(self, exportselection=0, textvariable=self.v_time).grid(column=1, row=1)

        tk.Button(self, text="Cancel", command = self.done).grid(column=0,row=2)
        tk.Button(self, text="Save", command = self.configure).grid(column=1,row=2)

    def configure(self):
        self.time = self.v_time.get()
        self.temp = self.v_temp.get()
        self.controller.configure(self.time, self.temp)
        self.done()

    def update_config(self, config):
        self.time = config.time
        self.temp = config.temp

class ConfigPort(tk.Frame):
    def __init__(self, done, controller, *args, **kwargs):
        """ Configuration panel and actions.

        @param done: callback to run when finished configurationt task.
        @param controller: serial client to send configuration to.
        """

        self.done = done
        self.controller = controller
        super().__init__(*args, **kwargs)

        self.v_port = tk.StringVar()

        self.port = 'COM4'
        self.v_port.set(self.port)

        tk.Label(self, text="Serial Port").grid(column=0, row=0)
        tk.Entry(self, exportselection=0, textvariable=self.v_port).grid(column=1, row=0)

        tk.Button(self, text="Cancel", command = self.done).grid(column=0,row=1)
        tk.Button(self, text="Save", command = self.configure).grid(column=1,row=1)

    def configure(self):
        self.port = self.v_port.get()
        self.controller.connect(self.port)
        self.done()


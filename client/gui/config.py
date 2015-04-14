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

        self.v_h = tk.IntVar()
        self.v_m = tk.IntVar()
        self.v_s = tk.IntVar()
        self.v_temp = tk.IntVar()

        self.time = 6*3600
        self.temp = 53
        self.v_h.set(self.time//3600)
        self.v_m.set((self.time%3600)//60)
        self.v_s.set(self.time%60)
        self.v_temp.set(self.temp)

        tk.Label(self, text="Heating Temperature (C)").grid(column=0, row=0)
        tk.Entry(self, exportselection=0, textvariable=self.v_temp).grid(column=1, row=0)

        tk.Label(self, text="Heating Time").grid(column=0, row=1)
        time_fr = tk.Frame(self)
        time_fr.grid(column=1, row=1)
        tk.Spinbox(time_fr, exportselection=0, textvariable=self.v_h, width=2, from_=0, to=96).pack(side=tk.LEFT)
        tk.Label(time_fr, text=":").pack(side=tk.LEFT)
        tk.Spinbox(time_fr, exportselection=0, textvariable=self.v_m, width=2, from_=0, to=59).pack(side=tk.LEFT)
        tk.Label(time_fr, text=":").pack(side=tk.LEFT)
        tk.Spinbox(time_fr, exportselection=0, textvariable=self.v_s, width=2, from_=0, to=59).pack(side=tk.LEFT)

        tk.Button(self, text="Cancel", command = self.done).grid(column=0,row=2)
        tk.Button(self, text="Save", command = self.save_config).grid(column=1,row=2)

    def save_config(self):
        self.time = self.v_h.get()*3600+self.v_m.get()*60+self.v_s.get()
        self.temp = self.v_temp.get()
        self.controller.oven_configure(self.time, self.temp)
        self.done()

    def update_config(self, config):
        self.time = config.time
        self.temp = config.temp
        self.v_h.set(self.time//3600)
        self.v_m.set((self.time%3600)//60)
        self.v_s.set(self.time%60)

        self.v_temp.set(self.temp)

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
        pe = tk.Entry(self, exportselection=0, textvariable=self.v_port)
        pe.grid(column=1, row=0)
        pe.bind('<Return>', self.save_config)
        tk.Button(self, text="Cancel", command = self.done).grid(column=0,row=1)
        tk.Button(self, text="Save", command = self.save_config).grid(column=1,row=1)

    def save_config(self, *args, **kwargs):
        self.port = self.v_port.get()
        self.controller.connect(self.port)
        self.done()


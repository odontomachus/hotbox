import tkinter as tk
import tkinter.filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import client

class StatusBar:
    """ A segmented status bar indicator 

    Options:
    @param parent: canvas object
    @param x0: left x coordinate
    @param y0: bottom y coordinate
    @param x1: right x coordinate
    @param y1: top y coordinate
    @param frac: fraction of bar to turn on [0-1]
    @param num: number of segments
    @param orientation: vertical or horizontal
    """
    def __init__(self, parent, x0, y0, x1, y1, frac=0, num=10, orientation="horizontal"):
        self.parent = parent
        self.ids = []
        self.num = num

        # width and height of segments.
        # Leave one blank pixel on each end for border, and 2px between each segments.
        w,h = ((x1-x0-2)//num-2, y1-y0-2) if orientation == "horizontal" else (x1-x0-2, (y1-y0-2)//num-2)
        dx, dy = (w+2, 0) if orientation == "horizontal" else (0, h+2)
        print(w,h,dx,dy)
        # border
        parent.create_rectangle(x0,y0, x0+(num-1)*dx+w+2, y0+(num-1)*dy+h+2)

        # create segments
        for i in range(num):
            self.ids.append(parent.create_rectangle(x0+i*dx+1, y0+i*dy+1, x0+i*dx+w+1, y0+i*dy+h+1,
                                    outline="",
                                    width=0,
                                    fill="green",
                                    disabledfill="#BBB",
                                    state=tk.NORMAL if i < frac*num else tk.DISABLED
                                ))

    def set_fraction(self, frac):
        """ Set fraction of display to turn on.

        @param frac: fraction of segments to show. [0-1]
        """
        for (i, sid) in enumerate(self.ids):
            self.parent.itemconfigure(sid, state=tk.NORMAL if i < frac*self.num else tk.DISABLED)


class Display(tk.Frame):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = None
        self.logger = logger
        self.history = []
        self.bt_save = tk.Button(self, text='Save', command=self.save, state=tk.DISABLED)
        self.bt_save.pack()

        # Create dashboard and indicators
        self.dash = tk.Canvas(self, width = 200, height = 30)
        self.dash.pack()
        self.status_id = self.dash.create_oval(5,5,25,25,
            fill="green",
            disabledfill="red",
            state=tk.DISABLED)
        self.heating_bar = StatusBar(self.dash, 30,5,90,25,0)


    def save(self):
        """ Save log to a file. """
        filename = tk.filedialog.asksaveasfilename(defaultextension=".csv", title="Hotbox: Save Data")
        # cancel returns empty string
        if not filename:
            return
        # Try and save file.
        try:
            with open(filename, 'w') as out:
                for row in self.history:
                    out.write(str(row) + "\n")
        except Exception as e:
            self.logger.error("Cannot save file: {{filename}}".format(filename=filename))

    def state_change(self, state):
        # Only run if state changed
        if self.state == state:
            return
        self.state = state
        # reset history
        if state == client.STATE_ACTIVE:
            self.history = []
            self.bt_save['state'] = tk.NORMAL
            self.dash.itemconfigure(self.status_id, state=tk.NORMAL)
        else:
            self.dash.itemconfigure(self.status_id, state=tk.DISABLED)

    def run_message(self, data):
        self.history.append(data)
        frac = data.part/client.HB_CYCLE
        self.heating_bar.set_fraction(frac)


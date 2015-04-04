import tkinter as tk
import tkinter.filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import client


class Display(tk.Frame):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = None
        self.logger = logger
        self.history = []
        self.bt_save = tk.Button(self, text='Save', command=self.save, state=tk.DISABLED)
        self.bt_save.pack()

        self.plt_data = ([],[],[])
        
        # Create dashboard and indicators
        self.dash = tk.Canvas(self, width = 200, height = 30)
        self.dash.pack()
        self.status_id = self.dash.create_oval(5,5,25,25,
            fill="green",
            disabledfill="red",
            state=tk.DISABLED)
        self.heating_bar = StatusBar(self.dash, 30,5,90,25,0)

        # create graph
        self.ymin = self.ymax = None
        self.figure = Figure()
        self.plot = self.figure.add_subplot(111)
        self.plot.set_autoscaley_on(True)
        self.t1_plot, = self.plot.plot(self.plt_data[0], self.plt_data[1])
        self.t2_plot, = self.plot.plot(self.plt_data[0], self.plt_data[2])
        self.graph = FigureCanvasTkAgg(self.figure, self)
        self.graph.draw()
        self.graph.get_tk_widget().pack()

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
            # new run, clear old data
            self.history = []
            del self.plt_data[0][:],self.plt_data[1][:],self.plt_data[2][:]
            if hasattr(self, 'templine'):
                del self.templine
            self.ymax = self.ymin = None
            self.bt_save['state'] = tk.NORMAL
            self.dash.itemconfigure(self.status_id, state=tk.NORMAL)
        else:
            self.dash.itemconfigure(self.status_id, state=tk.DISABLED)

    def run_message(self, data):
        self.history.append(data)
        frac = data.part/client.HB_CYCLE

        # update heating percent bar
        self.heating_bar.set_fraction(frac)

        # update temp graph
        time = data.time - data.countdown
        # show last 10 minutes
        xmax = time+35 - ((time+5)%30)
        xmin = max(0, xmax-600)
        if self.ymax is None:
            self.ymax = max(data.goal+2, data.t1+2, data.t2+2)
            self.ymin = min(data.goal-2, data.t1-2, data.t2-2)
            self.templine, = self.plot.plot([0,data.time], [data.goal, data.goal], 'r--')
        else:
            self.ymax = max(self.ymax, data.goal+2, data.t1+2, data.t2+2)
            self.ymin = min(self.ymin, data.goal-2, data.t1-2, data.t2-2)
        self.plt_data[0].append(time)
        self.plt_data[1].append(data.t1)
        self.plt_data[2].append(data.t2)
        self.t1_plot.set_xdata(self.plt_data[0])
        self.t2_plot.set_xdata(self.plt_data[0])
        self.t1_plot.set_ydata(self.plt_data[1])
        self.t2_plot.set_ydata(self.plt_data[2])
        self.plot.set_xlim(xmin, xmax)
        self.plot.set_ylim(self.ymin, self.ymax)
        self.figure.canvas.draw()




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


import tkinter as tk
import tkinter.filedialog

import datetime

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
        self.plt_data = ([],[],[])
        
        # Create dashboard and indicators
        self.dash = tk.Canvas(self, width = 200, height = 60)
        self.dash.pack()
        self.dash.create_text(25, 35, text="Running")
        self.status_id = self.dash.create_oval(15,5,35,25,
            fill="green",
            disabledfill="red",
            state=tk.DISABLED)
        self.dash.create_text(130, 35, text="Heat")
        self.heating_bar = StatusBar(self.dash, 70,5,190,25,0,15)

        info_box = tk.Frame(self)
        info_box.pack()
        tk.Label(info_box, text="Time left:").grid(column=0,row=0)
        self.countdown = tk.StringVar()
        tk.Label(info_box, textvariable=self.countdown).grid(column=1,row=0)

        self.total_time = tk.StringVar()
        tk.Label(info_box, text="Run time:").grid(column=0,row=1)
        tk.Label(info_box, textvariable=self.total_time).grid(column=1,row=1)

        self.temp1 = tk.StringVar()
        self.temp2 = tk.StringVar()
        self.target_temp = tk.StringVar()
        tk.Label(info_box, text="Temp 1:", anchor='sw').grid(column=2,row=0)
        tk.Label(info_box, textvariable=self.temp1, anchor='sw').grid(column=3,row=0)
        tk.Label(info_box, text="Temp 2:", anchor='sw').grid(column=4,row=0)
        tk.Label(info_box, textvariable=self.temp2, anchor='sw').grid(column=5,row=0)
        tk.Label(info_box, text="Target temp:", anchor='sw').grid(column=2,row=1)
        tk.Label(info_box, textvariable=self.target_temp, anchor='sw').grid(column=3,row=1)



        # save button
        self.bt_save = tk.Button(self, text='Save', command=self.save, state=tk.DISABLED)
        self.bt_save.pack()

        # create graph
        self.ymin = self.ymax = None
        self.figure = Figure()
        self.plot = self.figure.add_subplot(111)
        self.plot.axes.autoscale(True, True, False)
        self.plot.axes.set_ymargin(0.01)
        self.plot.set_xlabel("Time")
        self.plot.set_ylabel("Temp (C)")
        tfmt = matplotlib.ticker.FuncFormatter(lambda x,_: str(datetime.timedelta(seconds=int(x))))
        self.plot.xaxis.set_major_formatter(tfmt)
        self.t1_plot, = self.plot.plot(self.plt_data[0], self.plt_data[1], label="Temp 1")
        self.t2_plot, = self.plot.plot(self.plt_data[0], self.plt_data[2], label="Temp 2")
        self.templine, = self.plot.plot([], [], 'r-.', label="Target temperature")
        self.plot.legend(loc="upper left")
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
            self.ymax = self.ymin = None
            self.bt_save['state'] = tk.NORMAL
            self.dash.itemconfigure(self.status_id, state=tk.NORMAL)
        else:
            self.dash.itemconfigure(self.status_id, state=tk.DISABLED)
            self.heating_bar.set_fraction(0)

    def run_message(self, data):
        self.history.append(data)
        frac = data.part/client.HB_CYCLE
        # update heating percent bar
        self.heating_bar.set_fraction(frac)

        self.countdown.set(str(datetime.timedelta(seconds=data.countdown)))
        self.temp1.set(str(data.t1) + "C")
        self.temp2.set(str(data.t2) + "C")

        # update temp graph
        time = data.time - data.countdown
        # show last 10 minutes
        xmax = time+35 - ((time+5)%30)
        xmin = max(0, xmax-600)
        if self.ymax is None:
            self.ymax = max(data.goal+2, data.t1+2, data.t2+2)
            self.ymin = min(data.goal-2, data.t1-2, data.t2-2)
            self.templine.set_xdata([0, data.time])
            self.templine.set_ydata([data.goal, data.goal])
            self.total_time.set(str(datetime.timedelta(seconds=data.time)))
            self.target_temp.set(str(data.goal) + "C")
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
        self.plot.relim(visible_only=True)
        self.plot.autoscale_view(False, False, True)
#        self.plot.set_ylim(self.ymin, self.ymax)
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


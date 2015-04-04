import tkinter as tk
import tkinter.filedialog

import client


class Display(tk.Frame):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = None
        self.logger = logger
        self.history = []
        self.bt_save = tk.Button(self, text='Save', command=self.save, state=tk.DISABLED)
        self.bt_save.pack()

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
            raise e
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

    def run_message(self, data):
        self.history.append(data)


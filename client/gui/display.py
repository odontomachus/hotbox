import tkinter as tk

class Display(tk.Frame):
    def __init__(self, logger, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = 'disconnected'
        self.logger = logger
        self.history = []

    def save(self):
        """ Save log to a file. """
        filename = tk.asksaveasfilename(defaultextension=".tsv", title="Hotbox: Save Data")
        # cancel returns empty string
        if not filename:
            return
        # Try and save file.
        try:
            with open(filename, 'w') as out:
                out.write(history)
        except:
            logger.error("Cannot save file: {{filename}}".format(filename=self.config.filename))

    def state_change(self, state):
        if self.state == state:
            return
        # reset history
        if state == 'running':
            self.history = []

    def run_message(self, data):
        self.history.append(data)


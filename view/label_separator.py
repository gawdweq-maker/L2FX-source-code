import tkinter as tk
from tkinter.ttk import Separator


class LabelSeparator(tk.Frame):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.label = None
        self.separator = None
        self.grid_columnconfigure(0, weight=1)

        self.text = text

        self.create_separator()
        self.create_label()

    def create_label(self):
        self.label = tk.Label(self, text=self.text)
        self.label.grid(row=0, column=0, sticky="w", padx=7)

    def create_separator(self):
        self.separator = Separator(self, orient='horizontal')
        self.separator.grid(row=0, column=0, sticky='ew')
from tkinter import Frame, Label, Entry, DoubleVar, StringVar
from tkinter.ttk import Progressbar

from kbdmou import Keyboard
from scripts.utils import validate_decimal
from f_clicker.KeyReader import KeyReader


class KeyRepeater(Frame):
    def __init__(self, master=None, root=None, callback=None, **kw):
        self.root = root
        self.progress_var = DoubleVar()
        self.delay_var = StringVar()
        self.on_change_callback = callback

        self.current = 0.0
        self.maximum = 0.0

        super().__init__(master, **kw)
        vcmd = (self.register(validate_decimal))

        self.frame = Frame(self)
        self.frame.pack()

        inner_frame = Frame(self.frame, borderwidth=2)
        inner_frame.pack(padx=2, pady=2, expand=1)

        self.key_reader = KeyReader(inner_frame, root=root, callback=self.on_change_callback)
        self.key_reader.grid(row=0, column=0)

        Label(inner_frame, text=' every ').grid(row=0, column=1)
        Entry(inner_frame, width=6, justify='center', validate='all', validatecommand=(vcmd, '%P'),
              textvariable=self.delay_var).grid(row=0, column=2)
        Label(inner_frame, text=' sec ').grid(row=0, column=3)

        self.progress = Progressbar(inner_frame, orient='horizontal', length=50, mode='determinate',
                                    variable=self.progress_var)
        self.progress.grid(row=0, column=4)
        self.delay_var.trace('w', self.on_delay_change)
        self.update_ui()

    def on_delay_change(self, *args):
        self.current = 0.0
        try:
            self.maximum = float(self.delay_var.get())
        except ValueError:
            self.maximum = 0.0
        self.update_ui()
        self.on_change_callback()

    def update_ui(self):
        self.progress_var.set(self.current)
        self.progress.configure(maximum=self.maximum)

    def reset(self):
        self.current = 0
        self.update_ui()
        self.set_highlight(False)

    def tick(self) -> bool:
        if self.key_reader.key:
            self.current += 0.01
            self.update_ui()
            if self.current >= self.maximum:
                key = self.key_reader.entry_var.get()
                Keyboard.input(f'<{key}>'.encode('utf-8'))
                self.current = 0.0
                self.progress_var.set(self.current)
                return True
            return False
        return True

    def set_highlight(self, highlight: bool):
        if highlight is True:
            self.frame.config(background='red')
        else:
            self.frame.config(background='SystemButtonFace')

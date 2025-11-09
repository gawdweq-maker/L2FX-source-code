from tkinter import Tk, LabelFrame, Frame, Label, StringVar, Button, Radiobutton, IntVar


class Action(Frame):
    def __init__(self, master=None, root=None, **kw):
        self.root = root

        super().__init__(master, **kw)
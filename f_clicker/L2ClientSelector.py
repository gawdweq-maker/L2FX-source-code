from ctypes import wintypes
from tkinter import StringVar
from tkinter.ttk import Combobox

from f_clicker.L2Clients import Listener, L2Clients


class L2ClientsSelector(Combobox, Listener):

    def __init__(self, master=None, l2clients: L2Clients = None, **kw):
        self.l2clients = l2clients
        self.l2clients.add_listener(self)
        self.selected_window_title = StringVar()
        super().__init__(master, textvariable=self.selected_window_title, **kw)

    def on_update(self):
        self['values'] = list(self.l2clients.values())

    def on_remove(self, hwnd: wintypes.HWND):
        if self.l2clients[hwnd] == self.selected_window_title.get():
            self.set('')

    def get_selected_hwnd(self):
        vk_map = {value: key for key, value in self.l2clients.items()}
        title = self.selected_window_title.get()
        if not title:
            return None
        return vk_map.get(title)

from ctypes import wintypes
from tkinter import StringVar
from tkinter.ttk import Combobox
from typing import Dict

import l2helper
from scripts.utils import trim_title
from telemetry import StatReport


class L2ClientsCombobox(Combobox):

    def __init__(self, master=None, **kw):
        self.root = master.winfo_toplevel()
        self.timer_id = None
        self.selected_window_title = StringVar()
        self.l2clients: Dict[wintypes.HWND, str] = {}

        super().__init__(master, textvariable=self.selected_window_title, **kw)
        self.update_combobox()
        self.timer_id = self.root.after(1, self.check_l2clients)

    def update_combobox(self):
        self['values'] = list(self.l2clients.values())

    def get_selected_hwnd(self) -> wintypes.HWND or None:
        vk_map = {value: key for key, value in self.l2clients.items()}
        title = self.selected_window_title.get()
        if not title:
            return None
        return vk_map.get(title)

    def add(self, hwid: wintypes.HWND, title: str):
        self.l2clients[hwid] = title
        self.update_combobox()

    def remove(self, hwnd: wintypes.HWND):
        if self.l2clients[hwnd] == self.selected_window_title.get():
            self.set('')
        del self.l2clients[hwnd]
        self.update_combobox()

    def discover_l2_clients(self):
        hwnd_list = l2helper.find_lineage2_windows()

        # clear inactive l2 windows
        for hwnd in list(self.l2clients.keys()):
            if hwnd not in hwnd_list:
                self.remove(hwnd)
            else:
                title = l2helper.get_window_title(hwnd)
                if title != self.l2clients[hwnd]:
                    self.add(hwnd, trim_title(title))

        # discover new l2 windows
        for hwnd in hwnd_list:
            if hwnd not in self.l2clients:
                title = l2helper.get_window_title(hwnd)
                self.add(hwnd, title)

                image_path = l2helper.hwnd_to_path(hwnd, origin="discover-new-l2")
                StatReport.send_server_info(image_path)
            else:
                # client = clients[hwnd]
                pass

    def check_l2clients(self):
        self.discover_l2_clients()
        self.timer_id = self.root.after(1000, self.check_l2clients)

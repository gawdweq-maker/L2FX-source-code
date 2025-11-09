from abc import abstractmethod, ABC
from ctypes import wintypes
from tkinter import Tk
from typing import Dict

import l2helper
from scripts.utils import trim_title


class Listener(ABC):
    @abstractmethod
    def on_update(self):
        pass

    @abstractmethod
    def on_remove(self, hwnd: wintypes.HWND):
        pass


class L2Clients(Dict[wintypes.HWND, str]):

    def __init__(self, root: Tk):
        self.root = root
        self.timer_id = self.root.after(1, self.check_l2clients)
        self.listeners = []
        self.activated = []
        super().__init__()

    def add_listener(self, listener: Listener):
        self.listeners.append(listener)

    def remove_listener(self, listener: Listener):
        self.listeners.remove(listener)

    def add(self, hwid: wintypes.HWND, title: str):
        self[hwid] = title
        for listener in self.listeners:
            listener.on_update()

    def remove(self, hwnd: wintypes.HWND):
        for listener in self.listeners:
            listener.on_remove(hwnd)

        del self[hwnd]
        for listener in self.listeners:
            listener.on_update()

    def discover_l2_clients(self):
        hwnd_list = l2helper.find_lineage2_windows()

        # clear inactive l2 windows
        for hwnd in list(self.keys()):
            if hwnd not in hwnd_list:
                self.remove(hwnd)
            else:
                title = l2helper.get_window_title(hwnd)
                if title != self[hwnd]:
                    self.add(hwnd, trim_title(title))

        # discover new l2 windows
        for hwnd in hwnd_list:
            if hwnd not in self:
                title = l2helper.get_window_title(hwnd)
                self.add(hwnd, title)
            else:
                # client = clients[hwnd]
                pass

    def check_l2clients(self):
        self.discover_l2_clients()
        self.timer_id = self.root.after(1000, self.check_l2clients)

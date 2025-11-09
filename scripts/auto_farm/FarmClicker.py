import threading
import time

from itertools import cycle
from tkinter import Frame

import l2helper
from f_clicker.KeyRepeater import KeyRepeater


class FarmClicker(Frame):
    def __init__(self, master=None, root=None, l2client=None, **kw):
        self.root = root
        self.l2client = l2client
        self.key_repeaters = []
        self.current_key = None
        self.key_it = None
        self.auto_farm = False
        self.hunt_zone = False

        super().__init__(master, **kw)

        for i in range(0, 2):
            repeater = KeyRepeater(master, root=root, callback=self.on_change_keys)
            repeater.pack(padx=0, pady=(0, 0), fill='x', anchor='nw')
            self.key_repeaters.append(repeater)

        threading.Thread(target=self.tick_loop).start()

    def on_change_keys(self):
        keys = [key for key in self.key_repeaters if key.key_reader.key]
        if keys:
            self.key_it = cycle(keys)
            if not self.current_key:
                self.current_key = next(self.key_it)

    def tick_loop(self):
        while True:
            start_time = time.time()
            if self.l2client.active:
                hwnd = self.l2client.hwnd
                if l2helper.is_window_active(hwnd):
                    if self.auto_farm is True and self.hunt_zone is True:
                        if self.current_key:
                            if self.current_key.tick() is True:
                                self.current_key.set_highlight(False)
                                self.current_key = next(self.key_it)
                            else:
                                self.current_key.set_highlight(True)
            elapsed_time = time.time() - start_time
            delay = 0.01 - elapsed_time
            if delay > 0:
                time.sleep(delay)
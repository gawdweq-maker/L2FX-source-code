import random
from tkinter import Frame, StringVar, Entry, Label

from scripts.utils import validate_number, log


class DelayEntry(Frame):
    def __init__(self, master=None, **kw):
        self._timer_min_var = StringVar()
        self._timer_max_var = StringVar()
        self.range_mode_enabled = False

        super().__init__(master, **kw)
        vcmd = (self.register(validate_number))
        entry_min = Entry(self, textvariable=self._timer_min_var, justify='center', width=5, validate='all',
              validatecommand=(vcmd, '%P'))
        entry_min.grid(row=0, column=0)
        entry_min.bind("<KeyRelease>", lambda e: self.on_key_release())

        self.entry_max = Entry(self, textvariable=self._timer_max_var, justify='center', width=5, validate='all',
              validatecommand=(vcmd, '%P'))
        self.entry_max.bind("<KeyRelease>", lambda e: self.on_key_release())
        Label(self, text='sec').grid(row=0, column=2)

    def on_key_release(self):
        self.event_generate("<<DelayChanged>>")

    def get(self) -> int or None:
        min_value = 0
        max_value = 0
        timer_min_str = self._timer_min_var.get()
        timer_max_str = self._timer_max_var.get()

        if timer_min_str:
            min_value = int(timer_min_str)
        if timer_max_str:
            max_value = int(timer_max_str)

        # if range mode is not enabled - use min value
        if not self.range_mode_enabled:
            return min_value

        # swap values if need
        if min_value > max_value:
            min_value, max_value = max_value, min_value

        # pick random value
        v = random.randint(min_value, max_value)
        # log(f'Next random delay value [{min_value}, {max_value}] -> {v}')
        return v

    @property
    def min(self) -> int:
        min_value = 0
        timer_min_str = self._timer_min_var.get()
        if timer_min_str:
            min_value = int(timer_min_str)
        return min_value

    @property
    def max(self) -> int:
        max_value = 0
        timer_max_str = self._timer_max_var.get()
        if timer_max_str:
            max_value = int(timer_max_str)
        return max_value

    def set(self, value: int or [int]):
        min_value = 0
        max_value = 0
        if isinstance(value, list) and len(value) == 2:
            min_value = value[0]
            max_value = value[1]
        elif isinstance(value, int):
            min_value = value
            max_value = value
        else:
            log(f'ERROR: can\'t set timer value "{value}" - must be int or [int, int]. Default value "0" will be used.')

        self._timer_min_var.set(str(min_value))
        self._timer_max_var.set(str(max_value))

    def range_mode(self):
        self.entry_max.grid(row=0, column=1, padx=(3, 0))
        self.range_mode_enabled = True

    def single_mode(self):
        self.entry_max.grid_forget()
        self.range_mode_enabled = False

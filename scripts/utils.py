import threading
from tkinter import Widget

import numpy as np
import time
from datetime import datetime
import sys
import io

from scripts import L2Bot
from view.btn_settings import SettingsButton


def log(msg: str, bot: L2Bot = None):
    cuid = f'[{bot.cuid}]' if bot else ''
    print(f'{datetime.now().strftime("%H:%M:%S.%f")} {cuid} {msg}')


# Pick nickname from window's title
def trim_title(title: str) -> str:
    idx = title.find(' -')
    return title[0:idx] if idx > 0 else title


def wait_or_condition(predicate, timeout: float):
    step = 0.1
    lock = threading.Lock()
    condition = threading.Condition(lock)
    with condition:
        for i in np.arange(0, timeout, step):
            if predicate():
                break
            time.sleep(step)


def enable_all_widgets(widget: Widget, enabled=True):
    if isinstance(widget, SettingsButton):
        return
    ignore = ['frame', 'progressbar']
    if not any(sub in widget.widgetName for sub in ignore):
        state = 'normal' if enabled else 'disabled'
        widget.configure(state=state)
    for child in widget.winfo_children():
        enable_all_widgets(child, enabled)


# function to validate value is number or empty
def validate_number(value, max_length=None):
    return str.isdigit(value) or value == ""


def validate_decimal(value):
    if value == "":
        return True

    try:
        num = float(value)
        if num < 0:
            return False

        if round(num * 10) != num * 10:
            return False
    except ValueError:
        return False

    return True


def validate_valhalla_pin(value):
    if len(value) > 8:
        return False
    return validate_number(value)


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = io.BytesIO()

    def __getattr__(self, attr):
        return getattr(self.terminal, attr)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(bytes(message, 'UTF-8'))

    def flush(self):
        pass


logger = Logger()
sys.stdout = logger

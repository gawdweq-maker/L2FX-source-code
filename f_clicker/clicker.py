import threading
import webbrowser
from itertools import cycle

import time
from tkinter import Tk, LabelFrame, Frame, Label, StringVar, Button, Radiobutton, IntVar

import config
import l2helper
from f_clicker.KeyRepeater import KeyRepeater
from f_clicker.L2ClientsCombobox import L2ClientsCombobox
from view.btn_start import StartStopButton
from view.ui import Icons


# Execution mode
MODE_PARALLEL = 0
MODE_SEQUENTIAL = 1


root = Tk()
key_repeaters = []
current_key = None
key_it = None
is_running = False


def start_handler():
    global is_running
    is_running = True


def stop_handler():
    global is_running
    is_running = False
    for r in key_repeaters:
        r.reset()


def on_change_mode():
    for r in key_repeaters:
        r.reset()


def on_change_keys():
    global current_key
    global key_it
    keys = [key for key in key_repeaters if key.key_reader.key]
    if keys:
        key_it = cycle(keys)
        if not current_key:
            current_key = next(key_it)


def tick_loop():
    global current_key
    global key_it
    global is_running

    while True:
        start_time = time.time()
        if is_running is True:
            hwnd = window_selector.get_selected_hwnd()
            if l2helper.is_window_active(hwnd):
                exec_mode = mode.get()
                if exec_mode is MODE_PARALLEL:
                    for r in key_repeaters:
                        r.tick()
                elif exec_mode is MODE_SEQUENTIAL:
                    if current_key:
                        if current_key.tick() is True:
                            current_key.set_highlight(False)
                            current_key = next(key_it)
                        else:
                            current_key.set_highlight(True)
        elapsed_time = time.time() - start_time
        delay = 0.01 - elapsed_time
        if delay > 0:
            time.sleep(delay)


root.title(f'L2FX: F-helper {config.APP_ID}')

# root.overrideredirect(True)
root.attributes('-toolwindow', True)
root.geometry('275x515')
root.attributes('-topmost', True)
# root.resizable(width=False, height=False)

scale = l2helper.get_windows_screen_scaling()
print(f'Windows Screen Scaling: {scale}')
root.tk.call('tk', 'scaling', scale * 1.30)

# Activate on
selected_window_title = StringVar()

groupbox_window = LabelFrame(root, text="Activate on")
groupbox_window.pack(fill="both", expand=False, padx=7, pady=(3, 3))

props = Frame(groupbox_window)
props.pack(padx=10, pady=(3, 3), fill='x', anchor='nw')

props.grid_columnconfigure(1, weight=1)
Label(props, text='Window').grid(row=0, column=0, sticky='w', padx=(0, 5))

window_selector = L2ClientsCombobox(props, state="readonly", width=30)
window_selector.grid(row=0, column=1, pady=(5, 5))

# Execution mode
mode = IntVar()
mode.set(MODE_PARALLEL)

groupbox_mode = LabelFrame(root, text="Execution mode")
groupbox_mode.pack(fill="both", expand=False, padx=7, pady=(0, 3))

mode_props = Frame(groupbox_mode)
mode_props.pack(padx=10, pady=(3, 3), fill='x', anchor='nw')

Radiobutton(mode_props, text="Parallel", variable=mode, value=MODE_PARALLEL, command=on_change_mode).grid(
    row=0, column=0, padx=5)
Radiobutton(mode_props, text="Sequential", variable=mode, value=MODE_SEQUENTIAL, command=on_change_mode).grid(
    row=0, column=1,
    padx=5)

# Hotkeys ###########################################################

groupbox_keys = LabelFrame(root, text="Keys")
groupbox_keys.pack(fill="both", expand=False, padx=7, pady=(0, 5))

for i in range(0, 10):
    repeater = KeyRepeater(groupbox_keys, root=root, callback=on_change_keys)
    repeater.pack(padx=0, pady=(0, 0), fill='x', anchor='nw')
    key_repeaters.append(repeater)

start_stop = StartStopButton(root, command_start=start_handler, command_stop=stop_handler)
start_stop.pack(ipadx=10, ipady=8)

# Status bar ########################################################

# Status bar
statusbar = Label(root, bd=1, relief='sunken', anchor='w')
statusbar.pack(side='bottom', fill='x')

# Hyperlink in bottom statusbar
Label(statusbar, text="Join our", borderwidth=0, anchor='w', padx=4).grid(row=0, column=0)
link = Button(statusbar, text="Discord", image=Icons.discord, compound='left', borderwidth=0, fg="blue",
              cursor="hand2")
link.grid(row=0, column=1)
link.bind("<Button-1>", lambda e: webbrowser.open_new("https://discord.gg/v5T7hHF9zs"))

Label(statusbar, text="or", borderwidth=0, anchor='w', padx=3).grid(row=0, column=2)

link_tg = Button(statusbar, text="Telegram", image=Icons.telegram, compound='left', borderwidth=0,
                 fg="#5EAEC1",
                 cursor="hand2")
link_tg.grid(row=0, column=3)
link_tg.bind("<Button-1>", lambda e: webbrowser.open_new("https://t.me/l2fx_essence_bot"))

if config.LICENSE_ID:
    statusbar.grid_columnconfigure(4, weight=1)
    Label(statusbar, text=f'ID: {config.LICENSE_ID}', borderwidth=0, padx=3, justify='left').grid(row=0,
                                                                                                  column=5,
                                                                                                  sticky='e')
threading.Thread(target=tick_loop).start()
root.mainloop()

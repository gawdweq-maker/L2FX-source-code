import threading
import time
import webbrowser
from datetime import datetime
from tkinter import Tk, Label, SUNKEN, W, BOTTOM, X, Button, LEFT, E

import config
import l2helper
from config.types import AppType
from farm_bot.L2Farm import L2Farm
from scripts import Properties
from view.ui import Icons


stop_threads = False
root = Tk()


def main_loop():
    global stop_threads
    global root
    while True:
        l2farm.run_all_scripts(lambda: stop_threads)
        time.sleep(1)
        if stop_threads:
            break

        if config.EXPIRES_AT < datetime.utcnow():
            stop_threads = True
            l2farm.close_all_clients()
            l2helper.msg_box(
                f'ERROR: Your license {config.LICENSE_ID} just expired.\r\nBot will be stopped.\r\nPlease prolong your license.',
                config.APP_NAME, l2helper.MB_ICONERROR)
            if root:
                root.destroy()
                root.quit()


def update_image():
    l2farm.update_image()
    if not stop_threads:
        root.after(l2farm.get_refresh_interval(), update_image)


max_clients_str = f'[max: {config.MAX_CLIENTS} clients]' if config.MAX_CLIENTS > 1 else ''
root.title(f'Cracked unlimited version')
# root.overrideredirect(True)
# root.attributes('-toolwindow', True)
scale = l2helper.get_windows_screen_scaling()
print(f'Windows Screen Scaling: {scale}')
root.tk.call('tk', 'scaling', scale * 1.30)
# root.geometry('300x695')
# root.attributes('-topmost', True)
# root.resizable(width=True, height=False)

# Farm frame
l2farm = L2Farm(root)
l2farm.pack()

# Status bar
statusbar = Label(root, bd=1, relief=SUNKEN, anchor=W)
statusbar.pack(side=BOTTOM, fill=X)

# Hyperlink in bottom statusbar
if config.APP_TYPE == AppType.L2FX:
    Label(statusbar, text="Бездарному далбаебу на L2FX привет!", borderwidth=0, anchor=W, padx=4).grid(row=0, column=0)

elif config.APP_TYPE == AppType.L2FX:
    Label(statusbar, text="Бездарному далбаебу на L2FX привет!", borderwidth=0, anchor=W, padx=4).grid(row=0, column=0)


thread = threading.Thread(target=main_loop)
thread.start()

update_image()
root.mainloop()
stop_threads = True
Properties.save_properties()
l2helper.unregister_kbd_hotkey()

print('Running cleanup...')

# thread.join()
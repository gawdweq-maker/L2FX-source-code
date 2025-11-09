import ctypes
from tkinter import Frame, Label, Tk
from tkinter.ttk import Notebook

import config
import l2helper
from scripts import Properties, FrameComponent, Settings
from farm_bot.core.L2Game import L2Game
from scripts.utils import trim_title, enable_all_widgets, log
from view.btn_report import ReportButton
from view.btn_settings import SettingsButton
from view.btn_start import StartStopButton

CALLBACK = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int)


class L2Farm(FrameComponent, SettingsButton.Listener):
    tabControl: Notebook
    msg_label: Label
    buttons: Frame
    clients: dict
    max_clients: int
    start_stop_btn: StartStopButton
    root: Tk
    cuid: int

    def __init__(self, master: Tk) -> None:
        super().__init__(master)
        self.clients = {}
        self.root = master
        self.cuid = 0
        self.tabControl = Notebook(master)
        self.tabControl.pack(expand=True, fill='both')
        self.tabControl.update()
        self.msg_label = Label(self.tabControl, text="Can't find Lineage 2 client running.")
        self.refresh_interval_ms = Properties.properties.settings.screen_capture_interval_ms

        # Button frame
        self.buttons = Frame(master)
        self.buttons.pack(fill='x', pady=5)
        enable_all_widgets(self.buttons, enabled=False)

        # Start/stop button
        self.start_stop_btn = StartStopButton(self.buttons)
        self.start_stop_btn.pack(ipadx=10, ipady=8)

        self.registered_callback = CALLBACK(self.hotkey_callback)
        l2helper.register_kbd_hotkey(self.registered_callback)

        # Report button
        ReportButton(self.buttons, master, self.get_current_l2client).place(relx=1, rely=0, x=-7, y=1, anchor='ne')

        SettingsButton(self.buttons, master, self).place(relx=0, rely=0, x=7, y=1, anchor='nw')

    def hotkey_callback(self, modifier, vk):
        # print("foo has finished its job (%d, %d)" % (modifier, vk))
        self.start_stop_btn.next_state()

    def discover_l2_clients(self):
        if self.tabControl is not None:
            hwnd_list = l2helper.find_lineage2_windows()

            # clear inactive l2 windows
            for hwnd in list(self.clients.keys()):
                if hwnd not in hwnd_list:
                    self.tabControl.forget(self.clients[hwnd].tab_id)
                    self.clients[hwnd].close()
                    del self.clients[hwnd]
                else:
                    title = l2helper.get_window_title(hwnd)
                    client = self.clients[hwnd]
                    if title != client.title:
                        self.tabControl.tab(client.tab_id, text=trim_title(title))

            # discover new l2 windows
            for hwnd in hwnd_list:
                if hwnd not in self.clients:
                    if len(self.clients) < config.MAX_CLIENTS:
                        self.cuid += 1
                        client = L2Game(self.tabControl, hwnd, self.is_farm_active, self.stop_bot, self.root, cuid=self.cuid)
                        self.tabControl.add(client, text=trim_title(client.title))
                        self.clients[hwnd] = client
                else:
                    client = self.clients[hwnd]
                    self.tabControl.tab(client.tab_id, text=trim_title(client.title))

            # Show/hide message label
            if len(self.clients) == 0:
                self.msg_label.pack(fill='both', expand=True)
                enable_all_widgets(self.buttons, enabled=False)
            else:
                self.msg_label.pack_forget()
                enable_all_widgets(self.buttons)

    def update_image(self):
        for hwnd, client in self.clients.items():
            client.update()

    def set_refresh_interval(self, interval_ms: int):
        self.refresh_interval_ms = interval_ms
        for hwnd, client in self.clients.items():
            client.set_refresh_interval(interval_ms)

    def get_refresh_interval(self) -> int:
        return self.refresh_interval_ms

    def run_all_scripts(self, terminate_predicate):
        self.discover_l2_clients()
        for hwnd, client in list(self.clients.items()):
            success = False
            while not success:
                if terminate_predicate():
                    return
                if client.enabled:
                    success = client.run_scripts()
                else:
                    success = True

    def get_current_l2client(self) -> L2Game or None:
        tab_id = self.tabControl.select()
        for hwnd, client in self.clients.items():
            if client.tab_id == tab_id:
                return client
        return None

    def is_farm_active(self) -> bool:
        return self.start_stop_btn.state == StartStopButton.State.STOP

    def stop_bot(self):
        self.start_stop_btn.stop()

    def close_all_clients(self):
        num = len(self.clients.items())
        if num > 0:
            for hwnd, client in self.clients.items():
                client.close()
                self.tabControl.forget(client.tab_id)
            self.clients.clear()
            self.msg_label.pack(fill='both', expand=True)
            enable_all_widgets(self.buttons, enabled=False)
            log(f'Gracefully closed {num} client(s)')

    def destroy(self) -> None:
        self.close_all_clients()
        super().destroy()

    def on_update_settings(self, settings: Settings):
        for hwnd, client in self.clients.items():
            client.on_update_settings(settings)

        interval = settings.screen_capture_interval_ms
        self.set_refresh_interval(interval)




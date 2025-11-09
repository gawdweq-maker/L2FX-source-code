from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import Button, Tk, TOP, Frame, LabelFrame, IntVar, LEFT, W, Checkbutton, StringVar
from tkinter.ttk import Scale, Label

import config
from kbdmou import Mouse, Keyboard

from scripts import L2Window, Properties
from view.ModalDialog import ModalDialog
from scripts.Properties import Settings
from view.topup import TopUpDialog
from view.ui import Icons


class SettingsDialog(ModalDialog):

    def __init__(self, parent: Tk):
        super().__init__(parent)
        self._root = parent

        # self.geometry(f'250x260')
        self.title("Settings")
        self.wm_attributes('-toolwindow', 1)
        self.resizable(width=False, height=False)
        self.withdraw()

        self.refresh_interval_value = IntVar()
        self.settings = Settings()
        self.timer_range_mode = IntVar()
        self.power_saving_mode = IntVar()
        self.advanced_res_settings = IntVar()
        self.advanced_farm_settings = IntVar()
        self.auto_clicker = IntVar()
        self.multi_profile = IntVar()

        if not config.CAPABILITIES.WINDOW_CAPTURE_2:
            overhead = LabelFrame(self, text='CPU overhead')
            speed = Label(overhead)
            speed.grid_columnconfigure(1, weight=1)
            Label(speed, text="Fast speed").grid(row=0, column=0, padx=8)
            Scale(speed, from_=50, to=1000, orient='horizontal', variable=self.refresh_interval_value, command=self.slider_changed, cursor="hand2").grid(row=0, column=1, pady=(5, 0), sticky="ew")
            Label(speed, text="Low CPU").grid(row=0, column=2, padx=8)
            self.value_label = Label(speed, text=self.get_refresh_interval(), image=Icons.cpu, compound=LEFT)
            self.value_label.grid(row=1, column=1, pady=(0, 5))
            speed.pack(expand=False, fill="both")

            power_save = Label(overhead)
            Label(power_save, image=Icons.energy).pack(padx=(5, 0), side=LEFT)
            Checkbutton(power_save, text="Power Saving Mode", variable=self.power_saving_mode, onvalue=1,
                        offvalue=0).pack(pady=(3, 3), side=LEFT)
            power_save.pack(expand=False, fill="both")

            overhead.pack(pady=(3, 3), padx=5, expand=False, fill="both")


        timer_mode = LabelFrame(self, text='Delay mode')
        Label(timer_mode, image=Icons.stopwatch, compound=LEFT).pack(padx=(5, 0), side=LEFT)
        Checkbutton(timer_mode, text="Use min/max delay range", variable=self.timer_range_mode, onvalue=1, offvalue=0).pack(pady=(3, 6), side=LEFT)
        timer_mode.pack(pady=(3, 3), padx=5, expand=False, fill="both")

        expert_mode = LabelFrame(self, text='Expert mode')
        Checkbutton(expert_mode, text="Multi-profile",
                    variable=self.multi_profile, onvalue=1, offvalue=0).pack(padx=(5, 0), pady=(3, 2), anchor='w')
        Checkbutton(expert_mode, text="Advanced auto-farm settings",
                    variable=self.advanced_farm_settings, onvalue=1, offvalue=0).pack(padx=(5, 0), pady=(3, 2), anchor='w')
        Checkbutton(expert_mode, text="Advanced resurrection settings",
                    variable=self.advanced_res_settings, onvalue=1, offvalue=0).pack(padx=(5, 0), pady=(3, 2), anchor='w')
        Checkbutton(expert_mode, text="Auto-clicker",
                    variable=self.auto_clicker, onvalue=1, offvalue=0).pack(padx=(5, 0), pady=(0, 5), anchor='w')
        expert_mode.pack(pady=(0, 3), padx=5, expand=False, fill="both")

        driver_info = LabelFrame(self, text='Drivers')
        drv_fr = Frame(driver_info)
        drv_fr.grid_columnconfigure(1, weight=1)

        if config.CAPABILITIES.USE_TETHER_DRIVER:
            self.__btn_mou_drv_text = StringVar()
            self.__btn_kbd_drv_text = StringVar()

            if Mouse.Driver.is_installed():
                self.__btn_mou_drv_text.set("Remove")
            else:
                self.__btn_mou_drv_text.set("Install")
            if Keyboard.Driver.is_installed():
                self.__btn_kbd_drv_text.set("Remove")
            else:
                self.__btn_kbd_drv_text.set("Install")

            # Mouse driver UI
            Label(drv_fr, image=Icons.mouse).grid(row=0, column=0, sticky=W)
            Label(drv_fr, text=Mouse.Driver.status).grid(row=0, column=1, padx=8, pady=2, sticky=W)
            self.__btn_mou_drv = Button(drv_fr, textvariable=self.__btn_mou_drv_text, width=7, height=1, command=self.mouse_drv_click)
            self.__btn_mou_drv.grid(row=0, column=2)

            # Keyboard driver UI
            Label(drv_fr, image=Icons.keyboard).grid(row=1, column=0, sticky=W)
            Label(drv_fr, text=Keyboard.Driver.status).grid(row=1, column=1, padx=8, pady=(3, 2), sticky=W)
            self.__btn_kbd_drv = Button(drv_fr, textvariable=self.__btn_kbd_drv_text, width=7, height=1, command=self.keyboard_drv_click)
            self.__btn_kbd_drv.grid(row=1, column=2)

            drv_fr.pack(padx=8, pady=(4, 8), expand=False, fill="both")
            driver_info.pack(pady=(0, 10), padx=5, expand=False, fill="both")

        license_info = LabelFrame(self, text='License')
        Label(license_info, image=Icons.key, compound=LEFT).pack(padx=(5, 0), side=LEFT)
        if config.EXPIRES_AT:
            fr = Frame(license_info)
            Label(fr, text="License ID:").grid(row=0, column=0, pady=(3, 0), sticky=W)
            Label(fr, text=config.LICENSE_ID).grid(row=0, column=1, padx=8, pady=(3, 0), sticky=W)
            Label(fr, text="License Type:").grid(row=1, column=0, pady=(2, 0), sticky=W)
            Label(fr, text=config.LICENSE_TYPE.name).grid(row=1, column=1, padx=8, pady=(2, 0), sticky=W)
            Label(fr, text="Expiration date:").grid(row=2, column=0, pady=(2, 0), sticky=W)
            self.label_expires_at = Label(fr, text=config.EXPIRES_AT.date())
            self.label_expires_at.grid(row=2, column=1, padx=8, pady=(2, 0), sticky=W)
            Label(fr, text="Remaining days:").grid(row=3, column=0, pady=(2, 0), sticky=W)
            delta = config.EXPIRES_AT - datetime.utcnow()
            self.label_days_left = Label(fr, text=delta.days)
            self.label_days_left.grid(row=3, column=1, padx=8, pady=(2, 0), sticky=W)
            fr.pack(side=LEFT)
            btn_new_command = Button(fr, text="Use code", image=Icons.topup, compound='left',
                                     command=self.open_top_up_dialog)
            btn_new_command.grid(row=4, column=0, padx=0, pady=(2, 10), ipadx=5, sticky=W)
        else:
            Label(license_info, text="No license information available").pack(pady=(14, 16), side=LEFT)

        license_info.pack(pady=(0, 10), padx=5, expand=False, fill="both")

        buttons = Frame(self)
        Button(buttons, text='OK', width=12, height=1, command=self.save_and_close).grid(row=0, column=0, padx=(0, 15))
        Button(buttons, text='Cancel', width=12, height=1, command=self.close_dialog).grid(row=0, column=1)
        buttons.pack(pady=(0, 10))

        self.load_settings()

        # Put dialog in center of parent window
        self.update()
        # self.geometry("+%d+%d" % (parent.winfo_rootx() + (parent.winfo_width()-self.winfo_reqwidth())/2,
        #                           parent.winfo_rooty() + (parent.winfo_height()-self.winfo_reqheight())/2))
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        self.resizable(False, False)

        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2) - 40
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.deiconify()

    def get_refresh_interval(self):
        return 'CPU: {: d}'.format(self.refresh_interval_value.get())

    def slider_changed(self, event):
        self.value_label.configure(text=self.get_refresh_interval())

    def load_settings(self):
        self.settings = Properties.get_settings()
        self.refresh_interval_value.set(self.settings.screen_capture_interval_ms)
        self.timer_range_mode.set(self.settings.timer_range_mode)
        self.power_saving_mode.set(self.settings.power_saving_mode)
        self.multi_profile.set(self.settings.multi_profile)
        self.advanced_res_settings.set(self.settings.advanced_res_settings)
        self.advanced_farm_settings.set(self.settings.advanced_farm_settings)
        self.auto_clicker.set(self.settings.auto_clicker_enabled)
        if not config.CAPABILITIES.WINDOW_CAPTURE_2:
            self.slider_changed(None)

    def save_settings(self):
        interval = self.refresh_interval_value.get()
        # self.l2farm.set_refresh_interval(interval)
        self.settings.screen_capture_interval_ms = interval
        if self.timer_range_mode.get() == 1:
            self.settings.timer_range_mode = True
        else:
            self.settings.timer_range_mode = False
        if self.power_saving_mode.get() == 1:
            self.settings.power_saving_mode = True
        else:
            self.settings.power_saving_mode = False
        if self.multi_profile.get() == 1:
            self.settings.multi_profile = True
        else:
            self.settings.multi_profile = False
        if self.advanced_res_settings.get() == 1:
            self.settings.advanced_res_settings = True
        else:
            self.settings.advanced_res_settings = False
        if self.advanced_farm_settings.get() == 1:
            self.settings.advanced_farm_settings = True
        else:
            self.settings.advanced_farm_settings = False
        if self.auto_clicker.get() == 1:
            self.settings.auto_clicker_enabled = True
        else:
            self.settings.auto_clicker_enabled = False
        Properties.save_properties()

    def save_and_close(self):
        self.save_settings()
        self.close_dialog()

    def mouse_drv_click(self):
        if Mouse.Driver.is_installed():
            Mouse.Driver.remove()
            self.__btn_mou_drv_text.set("Install")
        else:
            Mouse.Driver.install()
            self.__btn_mou_drv_text.set("Remove")

    def keyboard_drv_click(self):
        if Keyboard.Driver.is_installed():
            Keyboard.Driver.remove()
            self.__btn_kbd_drv_text.set("Install")
        else:
            Keyboard.Driver.install()
            self.__btn_kbd_drv_text.set("Remove")

    def open_top_up_dialog(self):
        dlg = TopUpDialog(self._root)
        self._root.wait_window(dlg)
        self.label_expires_at.config(text=config.EXPIRES_AT.date())
        delta = config.EXPIRES_AT - datetime.utcnow()
        self.label_days_left.config(text=delta.days)


class SettingsButton(Button):

    @abstractmethod
    class Listener(ABC):
        def on_update_settings(self, settings: Settings):
            pass

    _root: Tk
    listener: Listener
    __l2window: L2Window
    __get_current_l2client = None

    def open_settings_dialog(self):
        dlg = SettingsDialog(self._root)
        self._root.wait_window(dlg)
        self.listener.on_update_settings(dlg.settings)

    def __init__(self, master, root, settings_listener: Listener):
        super().__init__(master, text="Settings", image=Icons.gear, compound=TOP, borderwidth=0, fg="#555555",
                         cursor="hand2", command=self.open_settings_dialog)
        self._root = root
        self.listener = settings_listener

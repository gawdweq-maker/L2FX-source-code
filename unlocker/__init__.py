# from ctypes import CDLL
# from tkinter import Frame, Label, Misc, LabelFrame, LEFT, Checkbutton, Button, BooleanVar
#
# import config
# import l2helper
# from scripts.utils import enable_all_widgets
# from scripts import Properties
# from view.tooltip import CreateToolTip
# from view.ui import Icons
#
# unlocker_dll = CDLL(f'unlocker\\UL.dll')
#
#
# class Unlocker(Frame):
#     def __init__(self, master: Misc):
#         super().__init__(master)
#
#         groupbox_unlocker = LabelFrame(self, text="Remote control")
#         unlocker_icon = Label(groupbox_unlocker, image=Icons.unlocker, compound=LEFT)
#         unlocker_icon.grid(row=0, column=0, padx=(7, 0), pady=0)
#         settings = Properties.get_settings()
#         self.unlocker_val = BooleanVar(value=settings.unlocker_enabled)
#         Checkbutton(groupbox_unlocker, text="Remote Click Unlocker",
#                     variable=self.unlocker_val,
#                     command=self.on_update_unlocker).grid(row=0, column=1)
#         if config.CAPABILITIES.UNLOCKER is True:
#             if not config.CAPABILITIES.USE_TETHER_DRIVER:
#                 enable_all_widgets(groupbox_unlocker, False)
#                 Label(groupbox_unlocker, text='Tether required!   ', foreground='red').grid(row=0, column=2,
#                                                                                             padx=(7, 0), pady=(0, 5))
#
#             CreateToolTip(unlocker_icon,
#                           'Enable mouse clicks when playing via remote control.\n'
#                           'Bypass Active-AntiCheat remote protection.')
#         else:
#             CreateToolTip(unlocker_icon,
#                           'Enable mouse clicks when playing via remote control.\n'
#                           'Contact support, to activate!')
#             self.unlocker_val.set(False)
#             enable_all_widgets(groupbox_unlocker, False)
#             Button(groupbox_unlocker, text='Activate', command=self.btn_activate).grid(row=0, column=2, padx=(7, 0), pady=(0, 5))
#
#         groupbox_unlocker.pack(fill="both", expand=False, padx=7, pady=(0, 5))
#
#     @staticmethod
#     def btn_activate():
#         l2helper.msg_box('Please, contact support to unlock Remote Clicks.', 'L2FX', style=l2helper.MB_ICONINFORMATION)
#
#     def on_update_unlocker(self):
#         value = self.unlocker_val.get()
#
#         # if value is True:
#         #     unlocker_dll.InitializeKeyboardAndMouse()
#         # else:
#         #     unlocker_dll.StopHooks()
#
#         settings = Properties.get_settings()
#         settings.unlocker_enabled = value
#         Properties.save_properties()

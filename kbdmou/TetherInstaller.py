import time

import kbdmou
import l2helper
from kbdmou import Mouse, Keyboard

mou = Mouse.Driver.is_installed()
kbd = Keyboard.Driver.is_installed()
if not mou or not kbd:
    l2helper.msg_box("Before start, we will install Mouse and Keyboard drivers.", "L2FX",
                     l2helper.MB_ICONINFORMATION)
    if not mou:
        if not Mouse.Driver.install():
            l2helper.msg_box("Installing Virtual Mouse Driver failed. Please contact support.", "L2FX",
                             l2helper.MB_ICONERROR)
        time.sleep(3)
    if not kbd:
        if not Keyboard.Driver.install():
            l2helper.msg_box("Installing Virtual Keyboard Driver failed. Please contact support.", "L2FX",
                             l2helper.MB_ICONERROR)
        time.sleep(3)
if not kbdmou.connect_kbd_mou():
    l2helper.msg_box("Can't connect to Mouse or Keyboard. Please contact support.", "L2FX",
                     l2helper.MB_ICONERROR)
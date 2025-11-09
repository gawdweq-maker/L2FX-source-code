from ctypes import wintypes
from os.path import dirname, join, abspath, isfile
from tkinter import Misc, Tk

import time

import config
import l2helper
from .L2Client import L2Client
from .TeleportObserver import TeleportObserver
from kbdmou import Keyboard, Mouse
from scripts.copper import Crop
from scripts.utils import log


class L2Game(L2Client):

    def __init__(self, master: Misc, hwnd: wintypes.HWND, farm_active_predicate, stop_bot_predicate, root: Tk, cuid: int):
        self.teleport_observer = TeleportObserver(self)
        super().__init__(master, hwnd, farm_active_predicate, stop_bot_predicate, root, cuid)

    def update(self):
        super().update()
        if self.screenshot:
            img_width = self.screenshot.width
            img_height = self.screenshot.height

            if img_width > 0 and img_height > 0:
                if self.active:
                    self.teleport_observer.update()

    @property
    def tp_done(self) -> bool:
        if config.CAPABILITIES.WINDOW_CAPTURE_2:
            return l2helper.is_to_done(self.hwnd)
        else:
            return self.teleport_observer.get_and_reset_tp_done()

    @property
    def tp_in_progress(self) -> bool:
        if config.CAPABILITIES.WINDOW_CAPTURE_2:
            return l2helper.is_tp_in_progress(self.hwnd)
        else:
            return self.teleport_observer.tp_in_progress

    def tp_reset(self):
        self.teleport_observer.tp_done = False

    @property
    def auto_farm(self) -> bool:
        return self.locate_center([
            "scripts\\auto_farm\\img\\down_arrow_active.png",
            "scripts\\auto_farm\\img\\up_arrow_active.png"
        ], confidence=.9) or \
                self.locate_center([
                    "scripts\\auto_farm\\img\\assassin\\autofarm_on.png",
                    "scripts\\auto_farm\\img\\deathknight2\\autofarm_on.png",
                    "scripts\\auto_farm\\img\\innadril\\autofarm_on.png"
                ], confidence=.9, attempts=3)

    def is_welcome_dialog(self) -> bool:
        return self.locate_center("scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_tl.png",
                                  confidence=.8, crop=Crop.UI_WELCOME_DECOR_LEFT) \
            or self.locate_center("scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_tr.png",
                                  confidence=.8, crop=Crop.UI_WELCOME_DECOR_RIGHT)

    def open_my_tp_dialog(self) -> bool:
        self.activate()

        # Open map with alt+m if not opened
        self.switch_keyboard_to_english()
        self.close_all_dialogs()
        Keyboard.input(b'<alt+m>')

        if self.click_on_image("scripts\\auto_farm\\img\\btn_map_tp.png",
                               confidence=.8,
                               crop=Crop.UI_MAP_MY_TELEPORT_BTN,
                               attempts=25,
                               move_cursor=True):
            log('Open My Teleport dialog (click on button in Map)', bot=self)
            if self.locate_center('scripts\\auto_farm\\img\\btn_add_custom_tp.png',
                                  confidence=.95,
                                  crop=Crop.UI_MY_TELEPORT_ADD_CUSTOM_TP,
                                  attempts=25):
                return True
        return False

    def tp_to_spot(self, next_tp_icon) -> bool:
        if self.open_my_tp_dialog():
            # next_tp_icon = self.custom_tp.next_tp()
            tp_icon = self.locate_center(next_tp_icon,
                                         confidence=.95,
                                         crop=Crop.UI_MY_TELEPORT)
            if tp_icon:
                x, y = tp_icon
                Mouse.move_to(x, y)
                Mouse.click(x, y)
                time.sleep(.250)
                Mouse.double_click(x, y)
                time.sleep(.1)
                self.close_all_dialogs()
                return True
            else:
                log("Can't find bot`s teleport in the game. Trying the next one...", bot=self)
        else:
            log("Can't open My teleports. Will try the next time...", bot=self)
        self.close_all_dialogs()
        return False

    @property
    def is_valhalla(self) -> bool:
        path = l2helper.hwnd_to_path(self.hwnd, origin='valhalla-check')
        if not path:
            return False

        # check for valhalla name in path
        if 'valhalla' in path.lower():
            return True

        if 'asgard' in path.lower():
            return True

        if 'asgardmidgard' in path.lower():
            return True

        if 'funmmogames' in path.lower():
            return True

        # check for valhalla launcher
        parent_folder = abspath(join(dirname(path), ".."))
        if isfile(join(parent_folder, "EsseenceDarkLight.exe")) is True:
            return True

        if isfile(join(parent_folder, "ValhallaAge.exe")) is True:
            return True

        if isfile(join(parent_folder, "AsgardMidgardUpdater.exe")) is True:
            return True

        return False

    @property
    def is_l2players(self) -> bool:
        # path = l2helper.hwnd_to_path(self.hwnd, origin='l2players-check')
        # if not path:
        #     return False
        #
        # # check for valhalla name in path
        # if 'l2players' in path.lower():
        #     return True
        #
        # # check for valhalla launcher
        # parent_folder = abspath(join(dirname(path), ".."))
        # return isfile(join(parent_folder, "l2players.exe")) or isfile(join(parent_folder, "l2players (1).exe"))
        return False

    @property
    def is_l2skelth(self) -> bool:
        # path = l2helper.hwnd_to_path(self.hwnd, origin='l2skelth-check')
        # if not path:
        #     return False
        #
        # # check for valhalla name in path
        # if 'skelth' in path.lower():
        #     return True
        #
        # # check for valhalla launcher
        # parent_folder = abspath(join(dirname(path), ".."))
        # return isfile(join(parent_folder, "Skelth - Guardians.exe"))
        return False

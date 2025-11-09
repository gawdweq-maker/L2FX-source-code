import time
from tkinter import Label, Frame, Checkbutton, IntVar, Misc, Tk
from ctypes import wintypes
from typing import Tuple
from PIL import ImageTk, Image, ImageOps

import config
from kbdmou import Mouse, Keyboard
from scripts import L2Window, L2Bot, Properties, FrameComponent, Settings

import l2helper
from farm_bot.AccountsController import AccountsController
from scripts.Properties import Account
from scripts.auto_farm import AutoFarm
from scripts.auto_farm.AutoFarm2 import AutoFarm2
from scripts.auto_login import AutoLogin
from scripts.copper import Crop
from scripts.utils import wait_or_condition, enable_all_widgets, log
from telemetry import StatReport


class L2Client(L2Window, L2Bot, FrameComponent, AccountsController.Listener):
    __hwnd: wintypes.HWND
    __title: str
    __screenshot: Image
    __label: Label = None
    __thumbnail_frame: Frame = None
    __enabled: IntVar

    __active = None

    _last_active: bool = False
    _last_window_state: int
    __cuid: int
    _root: Tk
    _success: bool = True
    _desktop_hwnd = None

    def __init__(self, master: Misc, hwnd: wintypes.HWND, farm_active_predicate, stop_bot_predicate, root: Tk, cuid: int):
        super().__init__(master)
        self._root = root
        self.__hwnd = hwnd
        self.__active = farm_active_predicate
        self.__stop_bot = stop_bot_predicate
        self.__cuid = cuid
        self.__title = ''
        self.__screenshot = None
        self.__enabled = IntVar(master)
        self.__enabled.set(1)
        self._last_window_state = None
        self.account = None
        self.__closed = False

        self._desktop_hwnd = l2helper.get_desktop_hwnd()

        l2helper.create_window_observer(hwnd)

        self.__thumbnail_frame = Frame(self)
        self.__thumbnail_frame.pack(fill='x')

        self.__label = Label(self.__thumbnail_frame, text='\n\n\n\nLineage 2 window is minimized\n\n\n\n', borderwidth=0, background='tomato')
        self.__label.pack(fill='x', expand=True)

        self.cb_enabled = Checkbutton(self.__thumbnail_frame, text="Active", variable=self.__enabled,
                                 onvalue=1, offvalue=0)

        self.image_path = l2helper.hwnd_to_path(hwnd, origin='init-new-l2-client')

        if self.image_path:
            StatReport.send_server_info(self.image_path)

        account_repository = Properties.get_client(self.image_path)

        self._script_AutoLogin = AutoLogin(self, account_repository, self)
        if config.CAPABILITIES.SCRIPT_AUTO_FARM_2:
            self._script_AutoFarm = AutoFarm2(self, root, self)
        else:
            self._script_AutoFarm = AutoFarm(self, root, l2client=self)

        self.accounts = AccountsController(self, account_repository, self)
        # self.accounts.pack()

        self._script_AutoLogin.pack(fill="both", expand=False, padx=(0, 0))
        self._script_AutoFarm.pack(fill="both", expand=False, padx=(0, 0))

        if self.accounts.size == 0:
            enable_all_widgets(self._script_AutoLogin, enabled=False)
            enable_all_widgets(self._script_AutoFarm, enabled=False)
            enable_all_widgets(self.cb_enabled, enabled=False)

        self._script_AutoLogin.on_account_changed(self.accounts.account)
        self._script_AutoFarm.on_account_changed(self.accounts.account)

        self.on_update_settings(Properties.get_settings())
        self.update()

    def on_select_account(self, account: Account or None):
        if account:
            enable_all_widgets(self._script_AutoLogin, enabled=True)
            enable_all_widgets(self._script_AutoFarm, enabled=True)
            enable_all_widgets(self.cb_enabled, enabled=True)
        else:
            enable_all_widgets(self._script_AutoLogin, enabled=False)
            enable_all_widgets(self._script_AutoFarm, enabled=False)
            enable_all_widgets(self.cb_enabled, enabled=False)

        self._script_AutoLogin.on_account_changed(account)
        self._script_AutoFarm.on_account_changed(account)

    def on_update_settings(self, settings: Settings):
        # self.accounts.on_update_settings(settings)
        if settings.multi_profile is True:
            self.accounts.pack(before=self._script_AutoLogin)
        else:
            self.accounts.forget()

        self._script_AutoLogin.on_update_settings(settings)
        self._script_AutoFarm.on_update_settings(settings)

    def close(self):
        l2helper.release_window_observer(self.hwnd)
        self.__closed = True

    @property
    def hwnd(self):
        return self.__hwnd

    @property
    def title(self):
        return self.__title

    @property
    def screenshot(self):
        return self.__screenshot

    @property
    def tab_id(self):
        return self._w  # get tab_id

    @property
    def cuid(self) -> int:
        return self.__cuid

    @property
    def enabled(self) -> bool:
        return self.__enabled.get() == 1 and self.accounts.size > 0

    @property
    def in_game(self) -> bool:
        if self.locate_center([
            "scripts\\img\\ui_exp.png",
            "scripts\\img\\ui_exp_essence.png"
        ], confidence=.6, crop=Crop.UI_EXP):
            return True
        if self.locate_center([
            "scripts\\img\\ui_menu.png",
            "scripts\\img\\ui_menu_crusader.png"
        ], confidence=.8, crop=Crop.UI_MENU):
            return True
        return False

    def update(self):
        self.__title = l2helper.get_window_title(self.hwnd)
        self.__screenshot = l2helper.capture_window_observer(self.hwnd)

        # if self.__screenshot:
        #     img = Crop.LOGIN_SERVER_SELECT_BTN_ASSASSIN.value.crop(self.__screenshot)

        if self.__label is not None:
            if self.screenshot is None:
                self.__label.configure(image='')
                self.__label.image = None
            else:
                img_width = self.screenshot.width
                img_height = self.screenshot.height

                widget_width = self.__label.winfo_width()
                widget_height = int(img_height * widget_width / img_width)

                if widget_width > 0 and widget_height > 0:
                    resized_image = self.screenshot.resize((widget_width, widget_height))

                    if resized_image:
                        if not self.enabled:
                            resized_image = ImageOps.grayscale(resized_image)

                        thumbnail = ImageTk.PhotoImage(resized_image, master=self.__label)
                        self.__label.configure(image=thumbnail)
                        self.__label.image = thumbnail
                    else:
                        print(f'resized_image is None')

            # set Active checkbox on top of thumbnail
            w = self.__label.winfo_width()
            h = self.__label.winfo_height()
            self.cb_enabled.place(anchor='se', x=w, y=h)

    def set_refresh_interval(self, interval_ms: int):
        if not l2helper.set_window_observer_interval(self.hwnd, interval_ms):
            log(f'Can\'t update refresh interval')

    @property
    def active(self) -> bool:
        return self.__active() and self.__closed is False

    def stop(self):
        self.__stop_bot()

    def run_scripts(self) -> bool:
        # log('run_scripts')
        self.__title = l2helper.get_window_title(self.hwnd)

        if self.active:
            # Get current window state
            if not self._last_window_state:
                self._last_window_state = l2helper.get_show_cmd(self.hwnd)
                if self._last_window_state == 2:  # SW_SHOWMINIMIZED
                    l2helper.set_show_cmd(self.hwnd, 9)  # SW_RESTORE

            self._last_active = True
            prev_value = self.in_game
            if self.in_game:
                # if in-game screen - reset state of login module
                self._script_AutoLogin.reset()
                result = self._script_AutoFarm.run(self, self)
                # Transfer maybe_disconnected flag
                if self._script_AutoFarm.maybe_disconnected:
                    self._script_AutoLogin.maybe_disconnected = True
                    self._script_AutoFarm.maybe_disconnected = False
                    self._script_AutoFarm.just_resurrected = False
                return result
            else:
                result = self._script_AutoLogin.run(self, self)
                # If auto-login script did any actions - reset auto-farm script
                if result and prev_value != self.in_game:
                    self._script_AutoFarm.reset()
                return result

        elif self._last_active:
            self._script_AutoFarm.reset()
            self._script_AutoLogin.reset()
            self._last_active = False
            self._success = True

        return self._success

    def activate(self):
        if not l2helper.is_window_active(self.hwnd):
            log('activate window', bot=self)
            l2helper.set_show_cmd(self.hwnd, 9)
            l2helper.activate_window3(self.hwnd)
            wait_or_condition(lambda: self.screenshot, 5)

    def deactivate(self):
        if l2helper.is_window_active(self.hwnd):
            if self._desktop_hwnd:
                log('deactivate window', bot=self)
                l2helper.activate_window3(self._desktop_hwnd)

    def is_active(self) -> bool:
        return l2helper.is_window_active(self.hwnd)

    def switch_keyboard_to_english(self):
        l2helper.switch_keyboard_to_english(self.hwnd)

    def find_img(self, images, confidence=1.0, crops=None):
        self.__screenshot = l2helper.capture_window_observer(self.hwnd)
        if not self.__screenshot:
            return None

        if not isinstance(crops, list):
            crops = [crops]

        for crop in crops:
            if crop:
                img_box = crop.value.crop(self.__screenshot)
            else:
                img_box = self.__screenshot
            if not isinstance(images, list):
                images = [images]

            for i in images:
                pos = l2helper.locate_center(img_box, i, confidence=confidence)
                if pos is not None:
                    if hasattr(img_box, 'left') and hasattr(img_box, 'top'):
                        (x, y) = pos
                        return x + img_box.left, y + img_box.top
                    else:
                        return pos

        return None

    def window_center(self) -> Tuple[int, int] or None:
        pos = l2helper.client_center(self.hwnd)
        if pos is None:
            return None

        wnd = l2helper.client_to_screen(self.hwnd)
        if wnd is None:
            return None

        return wnd[0] + pos[0], wnd[1] + pos[1]

    def window_size(self) -> Tuple[int, int]:
        return l2helper.client_size(self.hwnd)

    def client_to_screen(self) -> Tuple[int, int]:
        return l2helper.client_to_screen(self.hwnd)

    def locate_center(self, img, confidence=1.0, attempts=1, crop=None) -> Tuple[int, int] or None:
        if self.__closed:
            return None

        self.__screenshot = l2helper.capture_window_observer(self.hwnd)
        if self.__screenshot is None:
            return None

        pos = None
        for t in range(attempts):
            pos = self.find_img(img, confidence=confidence, crops=crop)
            if pos:
                break
            time.sleep(0.1)

        if pos is None:
            return None

        wnd = l2helper.client_to_screen(self.hwnd)
        if wnd is None:
            return None

        return wnd[0] + pos[0], wnd[1] + pos[1]

    def click_on_image(self, img, confidence=1, attempts=1, crop=None, move_cursor=False) -> bool:
        pos = self.locate_center(img, confidence=confidence, attempts=attempts, crop=crop)
        if pos is not None:
            x, y = pos
            if move_cursor:
                Mouse.move_to(x-3, y-3)
                time.sleep(Mouse.human_click_duration())
                Mouse.move_to(x, y)
            Mouse.click(x, y)
            return True
        return False

    def double_click_on_image(self, img, confidence=1, attempts=1, crop=None, move_cursor=False) -> bool:
        pos = self.locate_center(img, confidence=confidence, attempts=attempts, crop=crop)
        if pos is not None:
            x, y = pos
            if move_cursor:
                Mouse.move_to(x-3, y-3)
                time.sleep(Mouse.human_click_duration())
                Mouse.move_to(x, y)
            Mouse.double_click(x, y)
            return True
        return False

    def mouse_move_on_image(self, img, confidence=1, attempts=1, crop=None) -> bool:
        pos = self.locate_center(img, confidence=confidence, attempts=attempts, crop=crop)
        if pos is not None:
            self.activate()
            x, y = pos
            Mouse.move_to(x, y)
            return True
        return False

    def mouse_click(self, pos: Tuple[int, int]):
        # orig_x, orig_y = Mouse.position()
        x, y = pos
        Mouse.click(x, y)
        # Mouse.move_to(orig_x, orig_y)

    def mouse_double_click(self, pos: Tuple[int, int]):
        # orig_x, orig_y = Mouse.position()
        x, y = pos
        Mouse.double_click(x, y)
        # Mouse.move_to(orig_x, orig_y)

    def dump_screen(self, file_name: str, crop=None):
        img = l2helper.capture_window_observer(self.hwnd)
        if img is None:
            return

        if crop:
            img = crop.value.crop(img)

        img.save(file_name)
        print(f'screen saved to {file_name}')

    def close_all_dialogs(self):
        for i in range(0, 5):
            Keyboard.input(b'<esc>')
            time.sleep(.2)

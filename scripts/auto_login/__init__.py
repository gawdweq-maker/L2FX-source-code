import sys
import traceback

import time
from tkinter import StringVar, Frame, NW, Label, Entry, W, Misc, LabelFrame, LEFT, messagebox

import l2helper
from farm_bot.core import L2Game
from kbdmou import Mouse, Keyboard
from scripts import L2Script, L2Window, Properties, L2Bot, FrameComponent, Settings
from telemetry import ErrorReport
from view.delay_entry import DelayEntry
from view.ui import Icons
from ..copper import Crop
from view.delay_timer import DelayTimer
from ..utils import log, validate_valhalla_pin


class AutoLogin(L2Script, FrameComponent):

    def __init__(self, master: Misc, client_properties: Properties.AccountRepository, game: L2Game):
        super().__init__(master)
        self.__last_screen = 0
        self._connecting_count = 0
        self.count = 0
        self.client_properties = client_properties
        self.account = None
        self.maybe_disconnected = False
        self.game = game

        self.server_screen_time = None  # choose server screen timestamp

        self.__username_var = StringVar()
        self.__password_var = StringVar()
        self.__valhalla_pin_var = StringVar()

        groupbox_login = LabelFrame(self, text="Login")
        groupbox_login.pack(fill="both", expand=False, padx=7, pady=(0, 5))

        props = Frame(groupbox_login)
        props.pack(padx=10, pady=(3, 7), fill='x', anchor=NW)

        props.grid_columnconfigure(1, weight=1)
        Label(props, text='Username').grid(row=0, column=0, sticky=W, padx=(0, 5))

        entry_username = Entry(props, textvariable=self.__username_var, width=30)
        entry_username.grid(row=0, column=1, sticky=W, pady=(0, 0))
        entry_username.bind("<KeyRelease>", lambda e: self.on_login_update(self.__username_var.get()))

        Label(props, text='Password').grid(row=1, column=0, sticky=W)

        entry_password = Entry(props, textvariable=self.__password_var, width=30, show='*')
        entry_password.grid(row=1, column=1, sticky=W, pady=(0, 0))
        entry_password.bind("<KeyRelease>", lambda e: self.on_pass_update(self.__password_var.get()))

        if game.is_valhalla:
            extra_props = Frame(groupbox_login)
            extra_props.pack(padx=5, pady=(0, 5), anchor=NW)
            Label(extra_props, text=' Valhalla pin-code ', image=Icons.valhalla, compound=LEFT).grid(row=0, column=0)
            vcmd = (self.register(validate_valhalla_pin))
            entry_pin = Entry(extra_props, textvariable=self.__valhalla_pin_var, width=8, validate='all', validatecommand=(vcmd, '%P'))
            entry_pin.grid(row=0, column=2, sticky=W, pady=(0, 0))
            entry_pin.bind("<KeyRelease>", lambda e: self.on_valhalla_pin_update(self.__valhalla_pin_var.get()))
            Label(extra_props, text=' (6-8 symbols)').grid(row=0, column=3, sticky=W)

        reconnect_delay_props = Frame(groupbox_login)

        Label(reconnect_delay_props, text=' Reconnect delay ', image=Icons.stopwatch, compound=LEFT).grid(row=0,
                                                                                                          column=0)
        self.reconnect_delay = DelayEntry(reconnect_delay_props)
        self.reconnect_delay.grid(row=0, column=1)
        self.reconnect_delay.bind("<<DelayChanged>>", lambda e: self.on_update_delay_timer(self.reconnect_delay.min,
                                                                                           self.reconnect_delay.max))
        reconnect_delay_props.pack(padx=5, pady=(0, 5), anchor=NW)

        self.reconnect_delay_timer = DelayTimer(self.reconnect_delay)
        self.on_update_settings(Properties.get_settings())

    def on_update_settings(self, settings: Settings):
        if settings.timer_range_mode:
            self.reconnect_delay.range_mode()
        else:
            self.reconnect_delay.single_mode()

    def on_update_delay_timer(self, min_value, max_value):
        if self.account:
            self.account.reconnect_timer = [min_value, max_value]
            Properties.save_properties()

    def on_account_changed(self, account: Properties.Account):
        self.account = account
        if account:
            self.__username_var.set(account.login)
            self.__password_var.set(account.password)
            self.__valhalla_pin_var.set(account.valhalla_pin)
            self.reconnect_delay.set(account.reconnect_timer)
        else:
            self.__username_var.set('')
            self.__password_var.set('')
            self.__valhalla_pin_var.set('')
            self.reconnect_delay.set([0, 0])

    def on_login_update(self, login):
        if self.account:
            self.account.login = login
            Properties.save_properties()

    def on_pass_update(self, password):
        if self.account:
            self.account.password = password
            Properties.save_properties()

    def on_valhalla_pin_update(self, pin):
        if self.account:
            self.account.valhalla_pin = pin
            Properties.save_properties()

    def reset(self):
        self.__last_screen = 0
        self._connecting_count = 0
        self.reconnect_delay_timer.reset()
        self.server_screen_time = None

    def is_valhalla_pin_pad_error(self, l2window: L2Window) -> bool:
        exclamation = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                             confidence=.9,
                                             crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK)
        clear = l2window.locate_center("scripts\\auto_login\\img\\valhalla\\pin\\valhalla_num_b.png",
                                       confidence=.9,
                                       crop=Crop.VALHALLA_PIN_PAD_CLEAR)
        return bool(exclamation and clear)

    def is_valhalla_pin_pad(self, l2window: L2Window) -> bool:
        exclamation = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                      confidence=.9,
                                      crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK)
        clear = l2window.locate_center("scripts\\auto_login\\img\\valhalla\\pin\\valhalla_num_b.png",
                                  confidence=.9,
                                  crop=Crop.VALHALLA_PIN_PAD_CLEAR)
        return not exclamation and clear

    def valhalla_enter_pin(self, pin_code: str, l2window: L2Window) -> bool:
        pin_buttons = {}

        try:
            for number in pin_code:
                if number not in pin_buttons:
                    btn = l2window.locate_center([f'scripts\\auto_login\\img\\valhalla\\pin\\valhalla_num_{number}.png'],
                                                 confidence=.88,
                                                 crop=Crop.VALHALLA_PIN_PAD)
                    if btn:
                        pin_buttons[number] = btn

                btn = pin_buttons[number]
                if btn:
                    (x, y) = btn
                    Mouse.click(x, y)
                    time.sleep(0.025)
        except KeyError as e:
            stack_trace = traceback.format_exc()
            exc = sys.exc_info()
            ErrorReport.send("Pin error", f'KeyError: \'{exc[1]}\'', stack_trace, l2window.screenshot)
            messagebox.showerror("Error", "Can't enter PIN-code. Bot stopped. Please, contact support.")
            return False

        # click Accept
        btn = l2window.locate_center("scripts\\auto_login\\img\\valhalla\\pin\\valhalla_num_b.png",
                                     confidence=.9,
                                     crop=Crop.VALHALLA_PIN_PAD_CLEAR)
        if btn:
            (x, y) = btn
            Mouse.click(x - 90, y + 70)
            return True

        return False

    def run(self, l2window: L2Window, bot: L2Bot) -> True:
        # Do nothing if script is not enabled
        if not bot.active:
            self.reset()
            return True

        # log('run login script')

        if self.reconnect_delay_timer.is_running():
            log(f'Reconnection delay: {self.reconnect_delay_timer.count}/{self.reconnect_delay_timer.max} sec', bot=bot)
            return True

        chain_attempts = 1

        if self.maybe_disconnected:
            if not self.reconnect_delay_timer.is_started():
                self.reconnect_delay_timer.start()
                self.maybe_disconnected = False
            return True

        # Login/Password screen
        if self.__last_screen != 7:
            btn_enter_login = l2window.locate_center([
                "scripts\\auto_login\\img\\crusader\\ru\\btn_enter_login.png",  # RU
                "scripts\\auto_login\\img\\crusader\\en\\btn_enter_login.png",  # EN
                "scripts\\auto_login\\img\\crusader\\ru\\btn_exit_login.png",  # RU
                "scripts\\auto_login\\img\\crusader\\en\\btn_exit_login.png"  # EN
            ], confidence=.9, crop=Crop.LOGIN_PASS)

            if btn_enter_login is not None:
                self.server_screen_time = None
                username = bytes(self.__username_var.get(), 'UTF-8')
                password = bytes(self.__password_var.get(), 'UTF-8')

                log('Found login screen', bot=bot)
                self.reconnect_delay_timer.reset()

                l2window.activate()
                l2window.switch_keyboard_to_english()

                # if CAPS LOCK is on - then switch it off
                if l2helper.is_caps_lock_on():
                    Keyboard.input(b'<caps>')

                # if login input box is NOT selected switch with tab
                if not l2window.locate_center("scripts\\auto_login\\img\\focus_login.png", confidence=.95,
                                              attempts=9,
                                              crop=Crop.LOGIN_PASS):
                    Keyboard.input(b"<tab>")
                    if not l2window.locate_center("scripts\\auto_login\\img\\focus_login.png", confidence=.95,
                                                  attempts=9,
                                                  crop=Crop.LOGIN_PASS):
                        Keyboard.input(b"<tab>")

                time.sleep(0.1)
                Keyboard.input(b"<ctrl+A>")
                time.sleep(0.1)
                Keyboard.input(b'<backspace>')

                Keyboard.input(username, b"<tab>")

                time.sleep(0.1)
                Keyboard.input(b"<ctrl+A>")
                time.sleep(0.1)
                Keyboard.input(b'<backspace>')

                Keyboard.input(password, b"<enter>")
                chain_attempts = 10
                self.__last_screen = 1

        # interrupt is script disabled
        if not bot.active:
            self.reset()
            return True

        # Accept license screen
        if self.__last_screen != 2:
            btn_accept_license = l2window.locate_center([
                "scripts\\auto_login\\img\\crusader\\ru\\btn_accept_license.png",  # RU
                "scripts\\auto_login\\img\\crusader\\en\\btn_accept_license.png",  # EN
                "scripts\\auto_login\\img\\crusader\\ru\\btn_decline_license.png",  # RU
                "scripts\\auto_login\\img\\crusader\\en\\btn_decline_license.png"  # EN
            ], confidence=.9, attempts=chain_attempts, crop=Crop.LOGIN_LICENSE)

            if btn_accept_license is not None:
                log('Found license screen', bot=bot)
                l2window.activate()
                Keyboard.input(b"<enter>")
                # x, y = btn_accept_license
                # Mouse.click(x, y)
                chain_attempts = 10
                self.__last_screen = 2

                # Check if license wasn't accepted with Enter, try to accept with Mouse click
                time.sleep(1)
                btn_accept_license = l2window.locate_center([
                    "scripts\\auto_login\\img\\crusader\\ru\\btn_accept_license.png",  # RU
                    "scripts\\auto_login\\img\\crusader\\en\\btn_accept_license.png"  # EN
                ], confidence=.9, attempts=chain_attempts, crop=Crop.LOGIN_LICENSE)
                if btn_accept_license is not None:
                    log('Found license screen again, try to use mouse to accept license ', bot=bot)
                    l2window.activate()
                    l2window.mouse_click(btn_accept_license)

        # interrupt if script disabled
        if not bot.active:
            self.reset()
            return True

        # Connection in progress
        if self.__last_screen != 3:
            btn_cancel = l2window.locate_center(
                ["scripts\\auto_login\\img\\connection_in_progress_btn.png",
                 "scripts\\auto_login\\img\\deathknight2\\connection_in_progress_btn.png"],
                confidence=.9,
                attempts=chain_attempts,
                crop=Crop.LOGIN_CONNECTION_IN_PROGRESS_BNT)

            if btn_cancel:
                log(f'Found connecting... [{self._connecting_count} seconds]', bot=bot)
                self._connecting_count += 1
                # after 10 sec - cancel
                if self._connecting_count > 10:
                    self._connecting_count = 0
                    l2window.activate()
                    x, y = btn_cancel
                    Mouse.double_click(x, y)
                    # restore perv cursor position to avoid button highlighting
                    y -= 30
                    Mouse.move_to(x, y)
                    self.__last_screen = 4
                return False

        # interrupt if script disabled
        if not bot.active:
            self.reset()
            return True

        # Disconnected dialog
        if self.__last_screen != 4:
            if self.is_valhalla_pin_pad_error(l2window) is False:
                exclamation_2_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark_2.png",
                                                           confidence=.9,
                                                           crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK_2)

                confirm_pos = None
                if not exclamation_2_pos:
                    confirm_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                         confidence=.9,
                                                         crop=Crop.DIALOG_NORMAL)
                if exclamation_2_pos or confirm_pos:
                    if not self.reconnect_delay_timer.is_started():
                        self.reconnect_delay_timer.start()

                    if self.reconnect_delay_timer.is_ended():
                        l2window.activate()

                        if exclamation_2_pos:
                            (x, y) = exclamation_2_pos
                            x += 0
                            y += 150
                            Mouse.double_click(x, y)
                            log('Accept to disconnected dialog', bot=bot)
                            time.sleep(1)
                            Mouse.move_to(x, y - 100)

                        if confirm_pos:
                            (x, y) = confirm_pos
                            x += 110
                            y += 85
                            Mouse.double_click(x, y)
                            log('Accept to disconnected dialog', bot=bot)
                            time.sleep(1)
                            Mouse.move_to(x, y - 100)

                        # self.__last_screen = 4
                        self.reconnect_delay_timer.reset()
                        return False
                    else:
                        log(f'Reconnection delay: {self.reconnect_delay_timer.count}/{self.reconnect_delay_timer.count} sec',
                            bot=bot)
                        return True  # switch to new window while waiting for the delay

        # interrupt if script disabled
        if not bot.active:
            self.reset()
            return True

        # Choose Valhalla server (ASGARD, MIDGARD or SUNRISE)
        if self.__last_screen != 5:
            valhalla_asgard = None
            valhalla_midgard = None
            valhalla_sunrise = None

            valhalla_asgard = l2window.locate_center("scripts\\auto_login\\img\\valhalla\\valhalla_asgard.png",
                                                   confidence=.9,
                                                   crop=Crop.VALHALLA_ASGARD)
            if not valhalla_asgard:
                valhalla_midgard = l2window.locate_center("scripts\\auto_login\\img\\valhalla\\valhalla_midgard.png",
                                                        confidence=.9,
                                                        crop=Crop.VALHALLA_MIDGARD)

                if not valhalla_midgard:
                    valhalla_sunrise = l2window.locate_center("scripts\\auto_login\\img\\valhalla\\valhalla_sunrise.png",
                                                        confidence=.9,
                                                        crop=Crop.VALHALLA_SUNRISE)

            if valhalla_asgard or valhalla_midgard or valhalla_sunrise:
                log('Found Valhalla ASGARD or MIDGARD or SUNRISE screen', bot=bot)
                l2window.activate()
                Keyboard.input(b"<enter>")
                chain_attempts = 10
                self.__last_screen = 5

        # interrupt if script disabled
        if not bot.active:
            self.reset()
            return True

        # Select server screen - choose the default one (first)
        if self.__last_screen != 6:
            choose_server_ui = None
            for t in range(chain_attempts):

                choose_server_ui = l2window.locate_center(
                    "scripts\\auto_login\\img\\crusader\\ui_choose_server_corner.png",
                    confidence=.8,
                    crop=Crop.LOGIN_SERVER_SELECT_CRUSADER_TOP_RIGHT_CORNER)
                if choose_server_ui:
                    break

                choose_server_ui = l2window.locate_center(
                    "scripts\\auto_login\\img\\assassin\\btn_choose_server.png",
                    confidence=.8,
                    crop=Crop.LOGIN_SERVER_SELECT_BTN_ASSASSIN
                )
                if choose_server_ui:
                    break
                time.sleep(0.1)

            if choose_server_ui:
                if not self.server_screen_time:
                    # First time see server screen
                    self.server_screen_time = time.time()
                    log('Found server screen', bot=bot)
                    l2window.activate()
                    Keyboard.input(b"<enter>")

                    btns = l2window.locate_center(["scripts\\auto_login\\img\\valhalla\\btn_accept.png",
                                                   "scripts\\auto_login\\img\\assassin\\btn_accept.png",
                                                   "scripts\\auto_login\\img\\assassin\\btn_cancel.png"],
                                                  confidence=.9,
                                                  crop=Crop.LOGIN_SERVER_SELECT_BTNS)
                    if btns:
                        (bx, by) = btns

                        # Additional click as fallback
                        (px, py) = l2window.client_to_screen()
                        (w, h) = l2window.window_size()
                        x = px + w / 2 - 50
                        y = by
                        Mouse.click(x, y)

                    chain_attempts = 10
                    # self.__last_screen = 5
                else:
                    time_passed = time.time() - self.server_screen_time
                    # After 10 sec - display message
                    if time_passed > 10:
                        log(f'Waiting for next screen. {int(time_passed)} seconds have passed', bot=bot)

                    # After 30 sec - retry cancel and retry login
                    if time_passed > 30:
                        btns = l2window.locate_center(["scripts\\auto_login\\img\\valhalla\\btn_accept.png",
                                                       "scripts\\auto_login\\img\\assassin\\btn_accept.png",
                                                       "scripts\\auto_login\\img\\assassin\\btn_cancel.png"],
                                                      confidence=.9,
                                                      crop=Crop.LOGIN_SERVER_SELECT_BTNS)
                        if btns:
                            log(f'Retrying login from the beginning', bot=bot)
                            (bx, by) = btns

                            # Additional click as fallback
                            (px, py) = l2window.client_to_screen()
                            (w, h) = l2window.window_size()
                            x = px + w / 2 + 50
                            y = by
                            Mouse.click(x, y)
                            self.server_screen_time = None
                        else:
                            log(f'Can\'t retry, "cancel" button not found', bot=bot)

        # Big dialog - server is full / please try again
        if l2window.click_on_image("scripts\\auto_login\\img\\btn_confirm.png",
                                   confidence=.9,
                                   crop=Crop.LOGIN_BIG_DIALOG):
            self.server_screen_time = None
            self.__last_screen = 0
            time.sleep(0.5)

            # Check for server screen
            if l2window.locate_center("scripts\\auto_login\\img\\assassin\\btn_choose_server.png",
                                      confidence=.8,
                                      attempts=3,
                                      crop=Crop.LOGIN_SERVER_SELECT_BTN_ASSASSIN):
                (btn_x, btn_y) = Crop.LOGIN_SERVER_SELECT_BTN_CANCEL.value.center_in_window(l2window.hwnd)
                log(f'Cancel login', bot=bot)
                Mouse.click(btn_x, btn_y)

            return False

        # No connection message box
        if self.__last_screen != 7:
            btn_accept_no_connection = l2window.locate_center([
                "scripts\\auto_login\\img\\crusader\\ru\\btn_accept_no_connection.png",  # RU
                "scripts\\auto_login\\img\\crusader\\en\\btn_accept_no_connection.png"  # EN
            ], confidence=.9, crop=Crop.DIALOG_NORMAL)

            if btn_accept_no_connection is not None:
                self.server_screen_time = None
                log('Found no connection message', bot=bot)
                l2window.activate()
                time.sleep(0.3)
                Keyboard.input(b"<enter>")
                # x, y = btn_accept_no_connection
                # Mouse.click(x, y)
                self.__last_screen = 7
                return False

        # interrupt if script disabled
        if not bot.active:
            self.reset()
            return True

        # Select character screen
        if self.__last_screen != 8:
            btn_start_game = l2window.locate_center([
                "scripts\\auto_login\\img\\btn_start_game_left.png"
            ], confidence=.9, attempts=chain_attempts, crop=Crop.LOGIN_CHAR_SELECT)

            if btn_start_game is not None:
                self.server_screen_time = None
                log('Found character screen', bot=bot)
                l2window.activate()
                Keyboard.input(b"<enter>")
                # x, y = btn_start_game
                # Mouse.move_to(x, y)
                # Mouse.click()
                chain_attempts = 10
                self.__last_screen = 8

        if self.__last_screen == 8:
            if self.is_valhalla_pin_pad(l2window):
                log("Found Valhalla Pin pad -> input PIN", bot=bot)
                pin = self.__valhalla_pin_var.get()
                if pin and len(pin) > 0:
                    if 6 <= len(pin) <= 8:
                        if self.valhalla_enter_pin(pin, l2window) is True:
                            # wait for result
                            time.sleep(0.75)
                            if l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK):
                                log("Entered wrong Valhalla pin-code -> Stop bot (Please correct your pin-code)", bot=bot)
                                bot.stop()
                                return True
                        else:
                            log("Failed to enter pin-code -> Stop bot", bot=bot)
                            bot.stop()
                            return True
                    else:
                        log("Valhalla pin-code must be 6-8 symbols. Please enter correct pin-code.", bot=bot)
                        bot.stop()
                        return True
                else:
                    log("Valhalla pin-code not found. Please configure pin-code.", bot=bot)
                    bot.stop()
                    return True


        # Close login dialogs

        # Close in-game dialogs right after login
        if self.__last_screen == 8:
            btn_close_dlg = l2window.locate_center([
                "scripts\\auto_login\\img\\assassin\\btn_close_dlg.png",
                "scripts\\auto_login\\img\\crusader\\btn_close_dlg.png"
            ], confidence=.8, crop=Crop.DIALOG_NORMAL)
            if btn_close_dlg:
                log('Found in-game startup dialogs - close them', bot=bot)
                l2window.activate()
                l2window.close_all_dialogs()
                self.__last_screen = 9
            else:
                if l2window.locate_center([
                    "scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_l.png"
                ], confidence=.9, crop=Crop.UI_WELCOME_DECOR_LEFT) \
                        or l2window.locate_center([
                    "scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_r.png"
                ], confidence=.9, crop=Crop.UI_WELCOME_DECOR_RIGHT):
                    log('Found in-game deathknight2 startup dialogs - close them', bot=bot)
                    l2window.activate()
                    l2window.close_all_dialogs()
                    self.__last_screen = 9
                l2window.close_all_dialogs()

        # if self.__last_screen == 8:
        #     return True

        return False

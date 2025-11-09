import time
from tkinter import Frame, NW, Label, Misc, Tk, LabelFrame, LEFT, IntVar, Checkbutton

import config
import l2helper
from farm_bot.core import L2Client
from kbdmou import Keyboard, Mouse
from scripts import L2Script, L2Window, L2Bot, Properties, utils, FrameComponent
from scripts.auto_farm.auto_purchase import AutoPurchase
from scripts.custom_tp import CustomTp
from view.delay_entry import DelayEntry
from view.tooltip import CreateToolTip
from view.ui import Icons
from .FarmClicker import FarmClicker
from ..Properties import Account, Settings
from ..copper import Crop
from view.delay_timer import DelayTimer
from ..utils import log


class AutoFarm(L2Script, FrameComponent):
    __root: Misc
    _ui_reset: bool
    just_resurrected: bool
    first_run: bool

    custom_tp: CustomTp

    def __init__(self, master: Misc, root: Tk, l2client: L2Client):
        super().__init__(master)
        self.__root = master
        self._ui_reset = False
        self.just_resurrected = False
        self.first_run = True
        self.account: Account
        self._death_time = None
        self.maybe_disconnected = False
        self.need_for_tp = False
        self.res_btn = None
        self.res_for_adena = IntVar()
        self.res_to_clan_hall = IntVar()
        self.party_invite = IntVar()
        self.res_coin_frame = None
        self.res_to_clan_hall_frame = None
        self.party_invite_frame = None
        self._script_AutoPurchase = AutoPurchase()
        self.l2client = l2client
        self.hunt_zone = False
        self.auto_farm = False
        self.last_tp_time = None
        self.prev_auto_farm = None
        self.prev_is_training_buff = None
        self.next_training_check_time = 0
        self.anti_admin_check_after = 0
        self.power_saving_mode = False

        # Teleport group
        groupbox_tp = LabelFrame(self, text="Teleport")
        groupbox_tp.pack(fill="both", expand=False, padx=7, pady=(0, 0))

        tp_delay_props = Frame(groupbox_tp)
        Label(tp_delay_props, text=' Delay before teleport ', image=Icons.stopwatch, compound=LEFT).grid(row=0,
                                                                                                         column=0)
        self.tp_delay = DelayEntry(tp_delay_props)
        self.tp_delay.grid(row=0, column=1)
        self.tp_delay.bind("<<DelayChanged>>", lambda e: self.on_update_tp_delay(self.tp_delay.min, self.tp_delay.max))
        tp_delay_props.pack(padx=5, pady=(2, 2), anchor=NW)

        self.tp_buffs = Frame(groupbox_tp)
        skill_tp_icon = Label(self.tp_buffs, image=Icons.skill_teleport, compound=LEFT)
        skill_tp_icon.grid(row=0, column=0)
        self.random_tp_val = IntVar(value=1)
        self.anti_admin_protection_cb = Checkbutton(self.tp_buffs, text="Random teleport",
                                                    onvalue=1,
                                                    offvalue=0,
                                                    variable=self.random_tp_val,
                                                    command=self.on_update_random_tp)
        self.anti_admin_protection_cb.grid(row=0, column=1)
        self.tp_buffs.pack(padx=6, pady=(2, 0), anchor=NW)
        CreateToolTip(skill_tp_icon,
                      'Bot will use random teleport\n'
                      'from the list.')

        self.custom_tp = CustomTp(groupbox_tp, root)

        # Farm group
        self.groupbox_autofarm = LabelFrame(self, text="Farm")

        autofarm_delay_props = Frame(self.groupbox_autofarm)
        Label(autofarm_delay_props, text=' Delay before auto-farm ', image=Icons.stopwatch, compound=LEFT).grid(row=0,
                                                                                                                column=0)
        self.autofarm_delay = DelayEntry(autofarm_delay_props)
        self.autofarm_delay.grid(row=0, column=1)
        self.autofarm_delay.bind("<<DelayChanged>>", lambda e: self.on_update_autofarm_delay(self.autofarm_delay.min,
                                                                                             self.autofarm_delay.max))
        autofarm_delay_props.pack(padx=5, pady=(2, 0), anchor=NW)
        autofarm_delay_props.pack_forget()

        self.anti_admin_frame = Frame(self.groupbox_autofarm)
        self.anti_admin_frame.pack(padx=6, pady=(2, 0), anchor=NW)
        action_alert_icon = Label(self.anti_admin_frame, image=Icons.action_alert, compound=LEFT)
        action_alert_icon.grid(row=0, column=0)
        self.anti_admin_protection_val = IntVar(value=0)
        self.anti_admin_protection_cb = Checkbutton(self.anti_admin_frame,
                                                    text="Anti-Admin-Protection",
                                                    variable=self.anti_admin_protection_val,
                                                    command=self.on_update_anti_admin_protection)
        self.anti_admin_protection_cb.grid(row=0, column=1)
        CreateToolTip(action_alert_icon,
                      'If admin disable Auto-hunt or\n'
                      'teleport to another location\n'
                      'bot will be stopped!')

        self.party_invite_frame = Frame(self.groupbox_autofarm)
        Label(self.party_invite_frame, image=Icons.party, compound=LEFT).grid(row=0, column=0)
        self.party_invite_frame.pack(padx=6, pady=(1, 5), anchor=NW)
        Checkbutton(self.party_invite_frame, text="Auto-accept party invite", variable=self.party_invite,
                    onvalue=1,
                    offvalue=0, command=self.on_update_party_invite).grid(row=0, column=1)

        # Auto-clicker
        self.groupbox_autoclicker = LabelFrame(self, text="Auto-clicker")
        self.farm_clicker = FarmClicker(self.groupbox_autoclicker, root=root, l2client=l2client)
        self.farm_clicker.pack(padx=0, pady=(0, 0), fill='x', anchor='nw')

        # Resurrection group
        groupbox_res = LabelFrame(self, text="Resurrection")
        groupbox_res.pack(fill="both", expand=False, padx=7, pady=(0, 5))

        res_delay = Frame(groupbox_res)
        Label(res_delay, text=' Resurrection delay ', image=Icons.stopwatch, compound=LEFT).grid(row=0, column=0)
        self.res_delay = DelayEntry(res_delay)
        self.res_delay.grid(row=0, column=1)
        self.res_delay.bind("<<DelayChanged>>",
                            lambda e: self.on_update_res_delay(self.res_delay.min, self.res_delay.max))
        res_delay.pack(padx=5, pady=(2, 0), anchor=NW)

        self.instant_res_frame = Frame(groupbox_res)
        instant_res_icon = Label(self.instant_res_frame, image=Icons.skill_resurrect, compound=LEFT)
        instant_res_icon.grid(row=0, column=0)
        self.instant_res_val = IntVar(value=0)
        self.instant_res_cb = Checkbutton(self.instant_res_frame,
                                          text="Instant resurrect in first 30 sec",
                                          variable=self.instant_res_val,
                                          command=self.on_update_instant_res)
        self.instant_res_cb.grid(row=0, column=1)
        CreateToolTip(instant_res_icon,
                      'Instantly resurrect the character\n'
                      'if killed within the first 30 seconds\n'
                      'after arriving to the farm spot.')

        self.res_coin_frame = Frame(groupbox_res)
        Label(self.res_coin_frame, image=Icons.coin, compound=LEFT).grid(row=0, column=0)
        Checkbutton(self.res_coin_frame, text="Use Adena for resurrection", variable=self.res_for_adena, onvalue=1,
                    offvalue=0, command=self.on_update_res_coins).grid(row=0, column=1)

        self.res_to_clan_hall_frame = Frame(groupbox_res)
        Label(self.res_to_clan_hall_frame, image=Icons.castle, compound=LEFT).grid(row=0, column=0)
        Checkbutton(self.res_to_clan_hall_frame, text="To Clan Hall / Castle / Fort", variable=self.res_to_clan_hall, onvalue=1,
                    offvalue=0, command=self.on_update_res_to_clan_hall).grid(row=0, column=1)

        self.on_update_settings(Properties.get_settings())

        self.tp_delay_timer = DelayTimer(self.tp_delay)
        # self.autofarm_delay_timer = DelayTimer(self.autofarm_delay)
        self.res_delay_timer = DelayTimer(self.res_delay)

    def on_update_settings(self, settings: Settings):
        self._script_AutoPurchase.on_update_settings(settings)
        if settings.timer_range_mode:
            self.tp_delay.range_mode()
            self.autofarm_delay.range_mode()
            self.res_delay.range_mode()
        else:
            self.tp_delay.single_mode()
            self.autofarm_delay.single_mode()
            self.res_delay.single_mode()
        if settings.advanced_res_settings:
            if self.instant_res_frame:
                self.instant_res_frame.pack(padx=6, pady=(2, 0), anchor=NW)
            if self.res_coin_frame:
                self.res_coin_frame.pack(padx=6, pady=(0, 0), anchor=NW)
            if self.res_to_clan_hall_frame:
                self.res_to_clan_hall_frame.pack(padx=6, pady=(0, 5), anchor=NW)
        else:
            if self.instant_res_frame:
                self.instant_res_frame.pack_forget()
            if self.res_coin_frame:
                self.res_coin_frame.pack_forget()
            if self.res_to_clan_hall_frame:
                self.res_to_clan_hall_frame.pack_forget()
        if settings.advanced_farm_settings:
            self.groupbox_autofarm.pack(fill="both", expand=False, padx=7, pady=(0, 5))
        else:
            self.groupbox_autofarm.pack_forget()
        if settings.auto_clicker_enabled:
            self.groupbox_autoclicker.pack(fill="both", expand=False, padx=7, pady=(0, 5))
        else:
            self.groupbox_autoclicker.pack_forget()
        self.power_saving_mode = settings.power_saving_mode

    def on_account_changed(self, account: Properties.Account):
        self._script_AutoPurchase.on_account_changed(account)
        if account:
            self.account = account
            self.custom_tp.on_account_changed(account)
            self.tp_delay.set(account.tp_timer)
            self.autofarm_delay.set(account.autofarm_timer)
            self.res_delay.set(account.death_timer)
            self.res_for_adena.set(account.res_for_adena)
            self.res_to_clan_hall.set(account.res_to_clan_hall)
            self.party_invite.set(account.party_invite)
            self.random_tp_val.set(account.random_teleport)
            self.instant_res_val.set(account.instant_res)
            # self.anti_admin_protection_val.set(account.anti_admin_protection)
            if self.res_to_clan_hall_frame:
                utils.enable_all_widgets(self.res_to_clan_hall_frame, account.res_for_adena)
        else:
            self.custom_tp.on_account_changed(account)
            self.tp_delay.set([0, 0])
            self.autofarm_delay.set([0, 0])
            self.res_delay.set([0, 0])
            self.res_for_adena.set(0)
            self.res_to_clan_hall.set(0)
            self.party_invite.set(0)
            self.random_tp_val.set(0)
            self.instant_res_val.set(0)
            self.anti_admin_protection_val.set(1)
            if self.res_to_clan_hall_frame:
                utils.enable_all_widgets(self.res_to_clan_hall_frame, False)
        # utils.enable_all_widgets(self.action_alert_cb, False)

    def on_update_tp_delay(self, min_value, max_value):
        if self.account:
            self.account.tp_timer = [min_value, max_value]
            Properties.save_properties()

    def on_update_autofarm_delay(self, min_value, max_value):
        if self.account:
            self.account.autofarm_timer = [min_value, max_value]
            Properties.save_properties()

    def on_update_res_delay(self, min_value, max_value):
        if self.account:
            self.account.death_timer = [min_value, max_value]
            Properties.save_properties()

    def on_update_res_coins(self):
        value = self.res_for_adena.get()

        if value == 1:
            if l2helper.msg_box(f'Your character will lose experience when resurrected for Adena', config.APP_NAME,
                                l2helper.MB_ICONWARNING | l2helper.MB_OKCANCEL) == l2helper.IDCANCEL:
                self.res_for_adena.set(0)
                value = 0

        utils.enable_all_widgets(self.res_to_clan_hall_frame, value)

        if self.account:
            self.account.res_for_adena = value
            Properties.save_properties()

    def on_update_res_to_clan_hall(self):
        value = self.res_to_clan_hall.get()

        if self.account:
            self.account.res_to_clan_hall = value
            Properties.save_properties()

    def on_update_party_invite(self):
        value = self.party_invite.get()

        if self.account:
            self.account.party_invite = value
            Properties.save_properties()

    def on_update_random_tp(self):
        value = self.random_tp_val.get()

        if self.account:
            self.account.random_teleport = value
            Properties.save_properties()

    def on_update_instant_res(self):
        value = self.instant_res_val.get()

        if self.account:
            self.account.instant_res = value
            Properties.save_properties()

    def on_update_anti_admin_protection(self):
        value = self.anti_admin_protection_val.get()

        if self.account:
            self.account.anti_admin_protection = value
            Properties.save_properties()

    def reset(self):
        self._script_AutoPurchase.reset()
        self.first_run = True
        self._ui_reset = False
        self.need_for_tp = False
        self.tp_delay_timer.reset()
        # self.autofarm_delay_timer.reset()
        self.res_delay_timer.reset()
        self.res_btn = None

    @staticmethod
    def is_training(l2window: L2Window) -> bool:
        training_buff = l2window.locate_center("scripts\\auto_farm\\img\\training_buff.png",
                                               confidence=.9)
        return True if training_buff else False

    @staticmethod
    def is_auto_farm_enabled(l2window: L2Window) -> bool or None:
        auto_farm_on = l2window.locate_center([
            "scripts\\auto_farm\\img\\down_arrow_active.png",
            "scripts\\auto_farm\\img\\up_arrow_active.png"
        ], confidence=.9) or \
               l2window.locate_center([
                   "scripts\\auto_farm\\img\\assassin\\autofarm_on.png",
                   "scripts\\auto_farm\\img\\deathknight2\\autofarm_on.png",
                   "scripts\\auto_farm\\img\\valhalla\\autofarm_on.png",
                   "scripts\\auto_farm\\img\\innadril\\autofarm_on.png",
                   "scripts\\auto_farm\\img\\skelth\\autofarm_on.png",
                   "scripts\\auto_farm\\img\\l2players\\autofarm_on.png"
               ], confidence=.9, attempts=3) or \
                      l2window.locate_center([
                          "scripts\\auto_farm\\img\\skelth\\autofarm_on.png",
                          "scripts\\auto_farm\\img\\l2players\\autofarm_on.png"
                      ], confidence=.98)

        auto_farm_off = None
        if not auto_farm_on:
            auto_farm_off = l2window.locate_center([
                "scripts\\auto_farm\\img\\assassin\\autofarm_off.png",
                "scripts\\auto_farm\\img\\deathknight2\\autofarm_off.png",
                "scripts\\auto_farm\\img\\valhalla\\autofarm_off.png",
                "scripts\\auto_farm\\img\\innadril\\autofarm_off.png",
                "scripts\\auto_farm\\img\\skelth\\autofarm_off.png",
                "scripts\\auto_farm\\img\\l2players\\autofarm_off.png"
            ], confidence=.9)

        if auto_farm_on:
            return True
        elif auto_farm_off:
            return False
        else:
            return None

    # @staticmethod
    # def find_exit_baltus_btn(l2window: L2Window):
    #     return l2window.locate_center('scripts\\auto_farm\\img\\btn_close_baltus.png',
    #                                   confidence=.9,
    #                                   crop=Crop.UI_CLOSE_BALTUS_BTN)

    @staticmethod
    def find_exit_instance_btn(l2window: L2Window):
        return l2window.locate_center('scripts\\auto_farm\\img\\instance_clock_right.png',
                                      confidence=.9,
                                      crop=[Crop.UI_INSTANCE_CLOCK_AREA])

    @staticmethod
    def cancel_unknown_invites(l2window: L2Window, bot: L2Bot):
        exclamation_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                 confidence=.9,
                                                 crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK)
        if exclamation_pos:
            gear_pos = l2window.locate_center("scripts\\auto_farm\\img\\icon_gear_resurrect.png",
                                              confidence=.9,
                                              crop=[Crop.DIALOG_RESURRECT_GEAR_1,
                                                    Crop.DIALOG_RESURRECT_GEAR_2,
                                                    Crop.DIALOG_RESURRECT_GEAR_3,
                                                    Crop.DIALOG_RESURRECT_GEAR_4])

            if not gear_pos:
                top_left = l2window.locate_center("scripts\\img\\btn_top_left.png",
                                                  confidence=.9,
                                                  crop=Crop.DIALOG_BTN_3_TOP_LEFT)
                bottom_right = l2window.locate_center("scripts\\img\\btn_bottom_right.png",
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_BTN_3_BOTTOM_RIGHT)
                if top_left and bottom_right:
                    log('Unknown confirm dialog (TvT, Res, etc.) -> Cancel', bot=bot)
                    (tlx, tly) = top_left
                    (brx, bry) = bottom_right

                    x = tlx + (brx - tlx) / 2
                    y = tly + (bry - tly) / 2
                    Mouse.click(x, y)
                    return True
        return False

    def open_my_tp_dialog(self, l2window: L2Window, bot: L2Bot) -> bool:
        l2window.activate()

        # Open map with alt+m if not opened
        l2window.switch_keyboard_to_english()
        l2window.close_all_dialogs()
        Keyboard.input(b'<alt+l>')
        Keyboard.input(b'<alt+m>')

        if l2window.click_on_image(["scripts\\auto_farm\\img\\btn_map_tp.png",
                                    "scripts\\auto_farm\\img\\btn_map_tp_focus.png"],
                                   confidence=.8,
                                   crop=Crop.UI_MAP_MY_TELEPORT_BTN,
                                   attempts=25,
                                   move_cursor=True):
            log('Open My Teleport dialog (click on button in Map)', bot=bot)
            # Close Actions dialog
            Keyboard.input(b'<alt+m>')
        else:
            log('No map dialog found', bot=bot)

        if l2window.locate_center('scripts\\auto_farm\\img\\btn_add_custom_tp.png',
                                      confidence=.95,
                                      crop=Crop.UI_MY_TELEPORT_ADD_CUSTOM_TP,
                                      attempts=25):
            return True
        log('My teleport dialog no found', bot=bot)
        return False

    @staticmethod
    def start_stop_auto_farm():
        if config.CAPABILITIES.Z_AUTO_FARM is True:
            Keyboard.input(b'<z>')
        else:
            Keyboard.input(b'<alt+z>')

    def get_accept_invite_dialog_button(self, l2window: L2Window):
        settings = Properties.get_settings()
        if settings.advanced_farm_settings is True and self.party_invite.get() == 1:

            question_mark_pos_2 = l2window.locate_center("scripts\\img\\icon_question_mark_2.png",
                                                         confidence=.9,
                                                         crop=Crop.DIALOG_PARTY_INVITE_QUESTION_MARK_2)
            if question_mark_pos_2:
                (x, y) = question_mark_pos_2
                return x - 60, y + 155

            exclamation_mark_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                          confidence=.9,
                                                          crop=Crop.DIALOG_PARTY_INVITE_EXCLAMATION_MARK)
            if exclamation_mark_pos:
                (x, y) = exclamation_mark_pos
                return x + 85, y + 85
        return None

    def get_res_confirm_dialog_button(self, l2window: L2Window, gear: bool, bot=None):
        exclamation_1 = None
        exclamation_2 = None
        exclamation_3 = None
        question_2 = None
        question_3 = None
        question_4 = None
        icon_confirm_pos = None

        question_2 = l2window.locate_center("scripts\\img\\icon_question_mark_2.png",
                                            confidence=.9,
                                            crop=Crop.DIALOG_RESURRECTION_QUESTION_MARK_2)

        if not question_2:
            question_3 = l2window.locate_center("scripts\\img\\icon_question_mark_2.png",
                                                confidence=.9,
                                                crop=Crop.DIALOG_RESURRECTION_QUESTION_MARK_3)
            if not question_3:
                question_4 = l2window.locate_center("scripts\\img\\icon_question_mark_2.png",
                                                    confidence=.9,
                                                    crop=Crop.DIALOG_RESURRECTION_QUESTION_MARK_4)
                if not question_4:
                    exclamation_1 = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                           confidence=.9,
                                                           crop=Crop.DIALOG_RESURRECTION_EXCLAMATION_MARK)
                    if not exclamation_1:
                        exclamation_2 = l2window.locate_center("scripts\\img\\icon_exclamation_mark_2.png",
                                                               confidence=.9,
                                                               crop=Crop.DIALOG_RESURRECTION_EXCLAMATION_MARK_2)
                        if not exclamation_2:
                            exclamation_3 = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                                   confidence=.9,
                                                                   crop=Crop.DIALOG_RESURRECTION_EXCLAMATION_MARK_3)

        if exclamation_1 or exclamation_2 or exclamation_3 or question_2 or question_3 or question_4:
            icon_confirm_pos = l2window.locate_center(["scripts\\auto_farm\\img\\icon_l_coin_confirm.png",
                                                       "scripts\\auto_farm\\img\\icon_adena_confirm.png",
                                                       "scripts\\auto_farm\\img\\eigis\\icon_res_coin_confirm.png"],
                                                      confidence=.9,
                                                      attempts=3,
                                                      crop=Crop.DIALOG_RESURRECTION_COIN)

        if exclamation_1:
            if bot:
                log('Confirm resurrection for L-coins', bot=bot)

            if icon_confirm_pos:
                if bot:
                    log("Resurrect confirm for L-coin, Adena or Res-coin ", bot=bot)
                (x, y) = icon_confirm_pos
                x += 110
                y += 45
                return x, y

        if question_2 and gear:
            if bot:
                log('Confirm resurrection for free (1)', bot=bot)

            # (x, y) = question_2
            # x -= 60
            # y += 70
            # return x, y
            Keyboard.input(b'<enter>')
            return None

        if exclamation_3 and gear:
            if bot:
                log('Confirm resurrection for free (2)', bot=bot)

            (x, y) = exclamation_3
            x += 90
            y += 85
            return x, y

        if question_3 and gear:
            if bot:
                log('Confirm resurrection for free (3)', bot=bot)

            (x, y) = question_3
            x -= 60
            y += 85
            return x, y

        if exclamation_2 or question_4:
            if icon_confirm_pos:
                if bot:
                    log("Confirm resurrection for L-coin, Adena or Res-coin ", bot=bot)
                (x, y) = icon_confirm_pos
                x += 90
                y += 55
                return x, y

        return None

    def get_res_dialog_button(self, l2window: L2Window, bot=None):
        gear_pos = None
        question_pos = None

        settings = Properties.get_settings()
        res_for_adena = settings.advanced_res_settings is True and self.res_for_adena.get() == 1
        res_to_clan_hall = settings.advanced_res_settings is True and self.res_to_clan_hall.get() == 1

        gear_pos = l2window.locate_center("scripts\\auto_farm\\img\\icon_gear_resurrect.png",
                                          confidence=.7,
                                          crop=Crop.DIALOG_RESURRECT_GEAR)
        question_pos = l2window.locate_center("scripts\\auto_farm\\img\\icon_question_mark.png",
                                              confidence=.7,
                                              crop=Crop.DIALOG_RESURRECT_QUESTION)

        # check for confirm resurrection dialog
        btn = self.get_res_confirm_dialog_button(l2window, gear_pos, bot=bot)
        if btn:
            return btn

        if not gear_pos or not question_pos:
            return None

        (gx, gy) = gear_pos
        (qx, qy) = question_pos

        # find distance between gear and question mark
        # based on distance compute number of buttons in range
        # each button increases distance to 29 pixels, so we
        # divide distance to get count of buttons
        #
        # Reference values:
        #   1 button delta = 52, 53
        #   2 button delta = 80
        #   3 button delta = 109 110
        #   4 button delta = 138
        delta = qy - gy
        btn_count = (int)(delta/29)

        if res_for_adena is True:
            (x, y) = gear_pos
            if res_to_clan_hall is True and btn_count > 1:
                if bot:
                    log('Resurrect to clan hall / castle / fortress', bot=bot)
                x = x - 80
                y = y + 52
                return x, y
            else:
                if bot:
                    log('Resurrect to the nearest village for adena', bot=bot)
                x = x - 80
                y = y + 23
                return x, y
        else:
            # Assassin res buttons with icons
            res_btn = l2window.locate_center(["scripts\\auto_farm\\img\\assassin\\icon_l_coin_resurrect.png",
                                             "scripts\\auto_farm\\img\\eigis\\icon_res_coin_resurrect.png"],
                                             confidence=.9,
                                             crop=Crop.DIALOG_RESURRECT)
            if res_btn:
                if bot:
                    log('Resurrect for L-coins (assassin) or Res-coins (eigis)', bot=bot)
                return res_btn

            (x, y) = question_pos
            if bot:
                log('Resurrect for free or L-coin', bot=bot)
            x = x + 70
            y = y + 60
            return x, y

    def is_delay_in_progress(self, l2window: L2Window, bot: L2Bot) -> bool:
        if self.tp_delay_timer.is_running():
            log(f'Teleportation delay: {self.tp_delay_timer.count}/{self.tp_delay_timer.max} sec', bot=bot)
            return True

        # if self.autofarm_delay_timer.is_running():
        #     auto_farm = AutoFarm.is_auto_farm_enabled(l2window)
        #     if auto_farm:
        #         log(f'Auto-farm is active - cancel delay', bot=bot)
        #         self.autofarm_delay_timer.reset()
        #     else:
        #         log(f'Auto-farm delay: {self.autofarm_delay_timer.count}/{self.autofarm_delay_timer.max} sec', bot=bot)
        #     return True

        if self.res_delay_timer.is_running():
            log(f'Resurrection delay: {self.res_delay_timer.count}/{self.res_delay_timer.max} sec', bot=bot)

            # Cancel unknown dialog during delay
            self.cancel_unknown_invites(l2window, bot)

            return True

        return False

    def run(self, l2window: L2Window, bot: L2Bot) -> bool:

        if not self.account:
            log('Profile not found. Please, configure your bot.', bot=bot)
            return True

        if not self._ui_reset:
            l2window.activate()
            log('reset UI', bot=bot)
            # reset UI to ensure everything is visible
            Keyboard.input(b'<alt+l>')
            # close login rewards dialog
            l2window.close_all_dialogs()
            time.sleep(1.5)
            self._ui_reset = True
            self.prev_auto_farm = None

        auto_farm = AutoFarm.is_auto_farm_enabled(l2window)

        if self.anti_admin_protection_val.get() == 1:
            now = time.time()
            if now >= self.next_training_check_time:
                is_training_buff = AutoFarm.is_training(l2window)
                if is_training_buff is True:
                    self.anti_admin_check_after = now + 9999999
                else:
                    if self.prev_is_training_buff is True:
                        self.anti_admin_check_after = now + 30
                        log('Anti-Admin-Protection enabled', bot=bot)
                self.prev_is_training_buff = is_training_buff
                self.next_training_check_time = now + 5     # 10 seconds later

            if self.prev_auto_farm is True and auto_farm is False:
                if now >= self.anti_admin_check_after:
                    log('Auto-farm disabled. Check if char is dead', bot=bot)
                    res_btn = self.get_res_dialog_button(l2window, bot=bot)
                    if not res_btn:
                        log('Auto-farm disabled. Check if char is dead in 3 seconds', bot=bot)
                        time.sleep(3)
                        res_btn = self.get_res_dialog_button(l2window, bot=bot)

                    if not res_btn:
                        bot.stop()
                        log('STOP BOT!', bot=bot)
                        return True

        self.prev_auto_farm = auto_farm

        self.farm_clicker.auto_farm = auto_farm is not None and auto_farm is not False

        is_instance = True if AutoFarm.find_exit_instance_btn(l2window) else False

        # Do nothing if script is not enabled
        if not bot.active:
            # stop auto farm
            if auto_farm:
                l2window.activate()
                Keyboard.input(b'<esc>')
                self.start_stop_auto_farm()
                time.sleep(0.1)
            return True

        if self.is_delay_in_progress(l2window, bot=bot) is True:
            return True

        # log('run auto_farm script')

        # Check if welcome dialog is on screen - close it
        welcome_left = l2window.locate_center("scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_l.png",
                                              confidence=.8, crop=Crop.UI_WELCOME_DECOR_LEFT)
        welcome_right = l2window.locate_center("scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_r.png",
                                               confidence=.8, crop=Crop.UI_WELCOME_DECOR_RIGHT)
        if welcome_left or welcome_right:
            log('Found welcome dialog, close it', bot=bot)
            l2window.activate()
            if welcome_left:
                (x, y) = welcome_left
                Mouse.click(x, y)
            elif welcome_right:
                (x, y) = welcome_right
                Mouse.click(x, y)
            l2window.close_all_dialogs()
            return False

        chain_attempts = 1
        peace_zone = False
        hunt_zone = False
        if l2window.locate_center([
            "scripts\\auto_farm\\img\\icon_waypoint_grey.png",
            "scripts\\auto_farm\\img\\icon_waypoint_red.png",
            "scripts\\auto_farm\\img\\icon_waypoint_brown.png",
        ], confidence=.95, crop=Crop.UI_MAP_WAYPOINT):
            hunt_zone = True
        self.farm_clicker.hunt_zone = hunt_zone

        if l2window.locate_center("scripts\\auto_farm\\img\\icon_waypoint_blue.png",
                                  confidence=.95,
                                  crop=Crop.UI_MAP_WAYPOINT):
            peace_zone = True

        # check if not game screen
        if not peace_zone and not hunt_zone:
            l2window.activate()

            if bot.active is False:
                return True

            # reset UI to ensure everything is visible
            Keyboard.input(b'<alt+l>')

            # Not peace zone, neither hunting zone, may be Map is minimized? Let's try to open radar
            log('Radar not found, may be hidden or minimized. Trying to open radar...', bot=bot)
            Keyboard.input(b'<alt+shift+r>')
            return True

        if not bot.active:
            return True

        # party invite dialog
        party_invite_btn = self.get_accept_invite_dialog_button(l2window)
        if party_invite_btn:
            if bot:
                log('Accept party invite', bot=bot)
            (x, y) = party_invite_btn
            Mouse.click(x, y)
            return True

        if self.instant_res_val.get() == 1:
            has_30_sec_passed = self.last_tp_time and time.time() - self.last_tp_time >= 30
        else:
            has_30_sec_passed = True

        # resurrection dialog
        if not self.res_delay_timer.is_started() or not self.res_btn:
            self.res_btn = self.get_res_dialog_button(l2window, bot=bot)
            if self.res_btn and not self.res_delay_timer.is_started():
                # if self.last_tp_time and has_30_sec_passed is True:
                if has_30_sec_passed is True:
                    self.res_delay_timer.start()
                    return True

        # Resurrection timer ended - press button
        if self.res_btn and (self.res_delay_timer.is_ended() or has_30_sec_passed is not True):
            new_res_btn = self.get_res_dialog_button(l2window)
            if new_res_btn:
                self.res_btn = new_res_btn

            if has_30_sec_passed is False:
                log('Passed less 30 second since tp -> instant resurrection', bot=bot)

            (x, y) = self.res_btn
            l2window.activate()
            Mouse.double_click(x, y)
            chain_attempts = 10

            self.res_btn = self.get_res_dialog_button(l2window, bot=bot)
            if self.res_btn:
                (x, y) = self.res_btn
                l2window.activate()
                Mouse.double_click(x, y)
                self.just_resurrected = True
                self.need_for_tp = True
                self.res_btn = None
                self.res_delay_timer.reset()
                return True

        # Any other confirm dialog (TvT invite, Skill Resurrection, etc.)
        if self.cancel_unknown_invites(l2window, bot) is True:
            return True

        if not bot.active:
            return True

        # If in city with instance result dialog - close it!
        if peace_zone:
            inst_result_decor_l = l2window.locate_center('scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_l.png',
                                                         confidence=.9,
                                                         attempts=chain_attempts,
                                                         crop=Crop.UI_INSTANCE_RESULTS_LEFT)
            if inst_result_decor_l:
                log('Found instance results dialog -> close it', bot=bot)
                l2window.activate()
                (x, y) = inst_result_decor_l
                x = x + 130
                y = y + 150
                Mouse.click(x, y)
                time.sleep(.5)
                return True

        # Is peace zone of the instance - exit!
        # if peace_zone:
        #     instance_icon = l2window.locate_center('scripts\\auto_farm\\img\\instance_clock.png',
        #                                            confidence=.9,
        #                                            crop=Crop.UI_INSTANCE_CLOCK)
        #     if instance_icon:
        #         log('In instance -> exit', bot=bot)
        #         x, y = instance_icon
        #         y = y + 50
        #         Mouse.double_click(x, y)
        #         time.sleep(.5)
        #         y = y + 150
        #         Mouse.move_to(x, y)
        #         chain_attempts = 10
        #
        #     if l2window.locate_center('scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_l.png',
        #                               confidence=.9,
        #                               attempts=chain_attempts,
        #                               crop=Crop.UI_INSTANCE_RESULTS_LEFT) or \
        #             l2window.locate_center('scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_r.png',
        #                                    confidence=.9,
        #                                    attempts=chain_attempts,
        #                                    crop=Crop.UI_INSTANCE_RESULTS_RIGHT):
        #         log('Found instance results dialog -> close it', bot=bot)
        #         Keyboard.input(b'<alt+w>')

        if not bot.active:
            return True

        # disconnection dialog
        exclamation_2_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark_2.png",
                                                   confidence=.9,
                                                   crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK_2)
        if exclamation_2_pos:
            log('Disconnected dialog -> Ok', bot=bot)
            l2window.activate()
            (x, y) = exclamation_2_pos
            Mouse.click(x, y + 155)
            self.maybe_disconnected = True
            self.just_resurrected = True
            self.prev_auto_farm = None
            time.sleep(1)
            Mouse.move_to(x, y)
            return True

        # old disconnection dialog
        exclamation_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                 confidence=.9,
                                                 crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK)
        if exclamation_pos:
            # If dialog is event invite (has progress bar), then skip it
            if l2window.locate_center("scripts\\img\\dlg_invite_event_progress_bar.png",
                                      confidence=.9,
                                      attempts=chain_attempts,
                                      crop=Crop.UI_EVENT_DLG_PROGRESS):
                log('Found TvT invite dialog -> ignore it', bot=bot)
                time.sleep(5)
            else:
                # Disconnect dialog (single button in dialog)
                top_left = l2window.locate_center("scripts\\img\\btn_top_left.png",
                                                  confidence=.9,
                                                  crop=Crop.DIALOG_BTN_1_TOP_LEFT)
                bottom_right = l2window.locate_center("scripts\\img\\btn_bottom_right.png",
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_BTN_1_BOTTOM_RIGHT)
                if top_left and bottom_right:
                    log('Disconnected dialog (old) -> Ok', bot=bot)
                    l2window.activate()
                    (tlx, tly) = top_left
                    (brx, bry) = bottom_right

                    x = tlx + (brx - tlx) / 2
                    y = tly + (bry - tly) / 2
                    Mouse.double_click(x, y)
                    self.maybe_disconnected = True
                    self.just_resurrected = True
                    self.prev_auto_farm = None
                    time.sleep(1)
                    Mouse.move_to(x, y - 100)
                    return True

        self.maybe_disconnected = False

        if not bot.active:
            return True

        # Activate autofarm panel at first run
        # if self.first_run:
        #     (x, y) = Mouse.position()
        #     autofarm_btn = l2window.locate_center([
        #         "scripts\\auto_farm\\img\\assassin\\autofarm_off.png",
        #         "scripts\\auto_farm\\img\\deathknight2\\autofarm_off.png",
        #         "scripts\\auto_farm\\img\\innadril\\autofarm_off.png",
        #
        #         "scripts\\auto_farm\\img\\assassin\\autofarm_on.png",
        #         "scripts\\auto_farm\\img\\deathknight2\\autofarm_on.png",
        #         "scripts\\auto_farm\\img\\innadril\\autofarm_on.png"
        #     ], confidence=.9, crop=Crop.UI_AUTO_FARM)
        #
        #     if autofarm_btn:
        #         log(f'Activated autofarm panel first time', bot=bot)
        #         (cx, cy) = l2window.window_center()
        #         (x, y) = autofarm_btn
        #         Mouse.click(x, y, clicks=2, interval=0.25, click_duration=0.25)
        #         Mouse.move_to(cx, cy)  # Move cursor to center to drop tips
        #         time.sleep(0.1)
        #         Mouse.move_to(x, y)  # Move cursor to previous position
        #         self.first_run = False
        #
        # if not bot.active:
        #     return True

        # just resurrected but not in town (Eigis - Bloody Swampland)
        if hunt_zone and not auto_farm:
            if self.just_resurrected or self.need_for_tp:
                if not l2window.locate_center('scripts\\auto_farm\\img\\btn_add_custom_tp.png',
                                              confidence=.95,
                                              crop=Crop.UI_MY_TELEPORT_ADD_CUSTOM_TP,
                                              attempts=chain_attempts):
                    log('On spot after resurrect -> open custom tp dialog', bot=bot)
                    # reset death timer if just resurrected
                    self.res_delay_timer.reset()

                    if self.open_my_tp_dialog(l2window, bot):
                        return True

        # Just resurrected in instance
        if is_instance is True:
            if self.just_resurrected or self.need_for_tp:
                instance_icon = AutoFarm.find_exit_instance_btn(l2window)
                if instance_icon:
                    # baltus_btn = AutoFarm.find_exit_baltus_btn(l2window)
                    # if baltus_btn:
                    #     log('Found Baltus -> close', bot=bot)
                    #     (x, y) = baltus_btn
                    #     Mouse.click(x, y)
                    #     time.sleep(.5)

                    log('Resurrected in instance -> exit', bot=bot)
                    x, y = instance_icon
                    y = y + 53
                    Mouse.click(x, y)
                    time.sleep(.5)
                    y = y + 150
                    Mouse.move_to(x, y)
                    chain_attempts = 10

                    time.sleep(.5)

        # if exit instance confirm dialog
        question_mark = l2window.locate_center("scripts\\img\\icon_question_mark_2.png",
                                               confidence=.9,
                                               attempts=chain_attempts,
                                               crop=Crop.UI_INSTANCE_CLOCK_AREA)
        if question_mark:
            log('Exit instance confirm dialog -> Confirm (2)', bot=bot)
            (x, y) = question_mark
            x = x - 60
            y = y + 80
            Mouse.click(x, y)
            # Keyboard.input(b'<enter>')
            self.just_resurrected = False
            self.need_for_tp = False
            return True

        top_left = l2window.locate_center("scripts\\img\\btn_top_left.png",
                                          confidence=.9,
                                          attempts=chain_attempts,
                                          crop=Crop.DIALOG_BTN_2_TOP_LEFT)
        bottom_right = l2window.locate_center("scripts\\img\\btn_bottom_right.png",
                                              confidence=.9,
                                              attempts=chain_attempts,
                                              crop=Crop.DIALOG_BTN_2_BOTTOM_RIGHT)
        if top_left and bottom_right:
            log('Exit instance confirm dialog -> Confirm (1)', bot=bot)
            (tlx, tly) = top_left
            (brx, bry) = bottom_right

            x = tlx + (brx - tlx) / 2
            y = tly + (bry - tly) / 2
            Mouse.click(x, y)
            self.just_resurrected = False
            self.need_for_tp = False
            return True

        # in town - open custom tp dialog
        if peace_zone and not self._death_time and is_instance is False:
            # if self._script_AutoPurchase.run(l2window, bot) is True:
            #     return True

            if not l2window.locate_center('scripts\\auto_farm\\img\\btn_add_custom_tp.png',
                                          confidence=.95,
                                          crop=Crop.UI_MY_TELEPORT_ADD_CUSTOM_TP,
                                          attempts=chain_attempts):
                log('In town -> open custom tp dialog', bot=bot)
                # reset death timer if just resurrected
                self.res_delay_timer.reset()

                if self.open_my_tp_dialog(l2window, bot):
                    return True

        if not bot.active:
            return True

        # L2Skelth teleport confirm dialog
        if l2window.is_l2skelth:
            skelth_tp_dialog = l2window.locate_center('scripts\\img\\icon_question_mark_2.png',
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_SKELTH_TELEPORT_QUESTION_MARK)
            if skelth_tp_dialog:
                log('Found L2Skelth TP confirmation dialog -> Confirm', bot=bot)
                (x, y) = skelth_tp_dialog
                y += 150
                x -= 55
                Mouse.click(x, y)
                return True

        if not bot.active:
            return True

        # custom tp dialog opened - tp on spot
        add_custom_tp = l2window.locate_center('scripts\\auto_farm\\img\\btn_add_custom_tp.png',
                                               confidence=.95,
                                               crop=Crop.UI_MY_TELEPORT_ADD_CUSTOM_TP,
                                               attempts=chain_attempts)
        if add_custom_tp and is_instance is False:
            # Char in hunting zone - we don't need custom tp - close dialog
            if hunt_zone and not self.just_resurrected and self.need_for_tp is False:
                log('Found custom tp dialog opened in hunting zone - close it', bot=bot)
                (x, y) = add_custom_tp
                Mouse.click(x+100, y)   # Additional click for MW
                l2window.close_all_dialogs()
                return False

            # Char in town - tp to farm spot
            else:
                if not self.tp_delay_timer.is_started():
                    log('Found custom tp dialog', bot=bot)
                    self.tp_delay_timer.start()

                if self.tp_delay_timer.is_ended():
                    log('Custom tp dialog -> tp to the farm spot', bot=bot)
                    l2window.activate()

                    if self.custom_tp.has_next_tp():
                        # Additional check to confirm we are in peace zone
                        if l2window.locate_center([
                            "scripts\\auto_farm\\img\\icon_waypoint_blue.png"
                        ], confidence=.95, crop=Crop.UI_MAP_WAYPOINT) or self.just_resurrected or self.need_for_tp:
                            self.just_resurrected = False
                            next_tp_icon = self.custom_tp.next_tp(self.random_tp_val.get())
                            pos = l2window.locate_center(next_tp_icon, confidence=.95, crop=Crop.UI_MY_TELEPORT)
                            if pos:
                                l2window.activate()
                                l2window.mouse_click(pos)
                                time.sleep(0.3)
                                l2window.mouse_double_click(pos)
                                time.sleep(5)
                                self.tp_delay_timer.reset()
                                self.need_for_tp = False
                                self.last_tp_time = time.time()
                                log(f'last tp time {self.last_tp_time}', bot=bot)

                                self.start_stop_auto_farm()
                                time.sleep(5)
                            else:
                                log("Can't find bot`s teleport in the game. Trying the next one...", bot=bot)
                        else:
                            log('Hunting zone detected, cancel teleportation', bot=bot)
                            Keyboard.input(b'<esc>')
                    else:
                        log('No custom teleport in bot. Please, configure your bot', bot=bot)
                else:
                    log(f'Teleportation delay(1): {self.tp_delay_timer.count}/{self.tp_delay_timer.max} sec', bot=bot)
                    return True

            return False

        if not bot.active:
            return True

        # if auto_farm:
        #     # reset autofarm timer on spot
        #     self.autofarm_delay_timer.reset()

        # we are on spot - close tp dialog and start auto farm
        if hunt_zone and \
                auto_farm is False and \
                self.just_resurrected is False and \
                not self._death_time and \
                self.res_delay_timer.is_started() is False and \
                self.need_for_tp is False:
            # reset tp timer on spot
            self.tp_delay_timer.reset()

            if not bot.active:
                return True

            # if not self.autofarm_delay_timer.is_started():
            #     log('On spot -> start delay timer', bot=bot)
            #     self.autofarm_delay_timer.start()
            #
            # if self.autofarm_delay_timer.is_ended():
            log('Start auto-farm', bot=bot)     # repeat

            l2window.activate()

            # Close My Teleport dialog and other dialogs
            l2window.close_all_dialogs()

            # start autofarm
            self.start_stop_auto_farm()
            time.sleep(5)  # wait to see if autofarm enabled

            # check if autofarm enabled
            auto_farm = AutoFarm.is_auto_farm_enabled(l2window)
            if not auto_farm:
                log('Failed to start auto-farm. Try with mouse click', bot=bot)
                if l2window.is_l2players:
                    if l2window.click_on_image([
                                "scripts\\auto_farm\\img\\l2players\\autofarm_off.png",
                            ], confidence=.98, attempts=3) is False:
                        log('Failed to start auto-farm with mouse click', bot=bot)
                else:
                    if l2window.click_on_image([
                               "scripts\\auto_farm\\img\\assassin\\autofarm_off.png",
                               "scripts\\auto_farm\\img\\deathknight2\\autofarm_off.png",
                               "scripts\\auto_farm\\img\\innadril\\autofarm_off.png"
                           ], confidence=.9, attempts=3) is False:
                        log('Failed to start auto-farm with mouse click', bot=bot)
            else:
                pass


            # log('On spot -> start auto farm', bot=bot)

            # l2window.activate()

            # # if My Teleport dialog is opened - close it
            # if l2window.locate_center('scripts\\auto_farm\\img\\btn_add_custom_tp.png',
            #                           confidence=.95,
            #                           crop=Crop.UI_MY_TELEPORT):
            #     # Close My Teleport dialog and other dialogs
            #     Keyboard.input(b'<alt+w>')

        # If Valhalla Online Reward Box - collect it
        # if l2window.is_valhalla:
        reward_box = l2window.locate_center("scripts\\auto_farm\\img\\valhalla\\online_reward_box.png",
                                            confidence=.9,
                                            attempts=1,
                                            crop=Crop.VALHALLA_ONLINE_REWARD_BOX)
        if reward_box:
            l2window.activate()
            time.sleep(3)
            log('Collected Valhalla Online Reward Box', bot=bot)
            (x, y) = reward_box
            Mouse.double_click(x, y)
            time.sleep(0.5)
            Mouse.move_to(x-200, y)
            return True

        # If random rewards dialog with chest is opened - close it
        rewards_lock = l2window.locate_center("scripts\\auto_farm\\img\\rewards_lock.png", confidence=.9, attempts=1,
                                              crop=Crop.UI_REWARDS_LOCK)
        if rewards_lock:
            l2window.activate()
            log('Found chest reward dialog - close it', bot=bot)
            (x, y) = rewards_lock
            Mouse.click(x, y)       # Additional click for MW
            Keyboard.input(b'<esc>')
            return True

        if self.power_saving_mode is True:
            if l2helper.get_idle_duration() > 30:
                l2window.deactivate()

        return True

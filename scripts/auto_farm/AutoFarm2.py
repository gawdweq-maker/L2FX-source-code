import time
from tkinter import Misc, Tk

from kbdmou import Mouse, Keyboard
from scripts import L2Window, L2Bot
from farm_bot.core import L2Game
from view.Timer import Timer
from scripts.auto_farm import AutoFarm
from scripts.auto_farm.InstanceZoneFarm import InstanceZoneFarm
from scripts.copper import Crop
from scripts.utils import log

STOP_SCRIPT = 99


class AutoFarm2(AutoFarm):

    def __init__(self, master: Misc, root: Tk, game: L2Game):
        super().__init__(master, root)

        self.game = game
        self.is_black_screen = False
        self.just_teleported = False
        self.expect_tp = False
        '''
            0: in town location -> tp to spot
            1: triggered teleport -> wait for tp (black screen)
            2: triggered resurrect -> tp to spot
        '''
        self.state = 0
        self.tp_done_timer = Timer(seconds=8)
        self.instance_zone_farm = InstanceZoneFarm()
        self.tvt_invite_dlg = False

    def reset(self):
        super().reset()
        self.tp_done_timer.reset()
        self.state = 0

    def handle_l2_dialog(self, l2window: L2Window, bot: L2Bot) -> bool:

        # Disconnect and Invite dialog exclamation mark
        exclamation_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                 confidence=.9,
                                                 crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK)
        if exclamation_pos:
            # If dialog is event invite (has progress bar), then skip it
            if l2window.locate_center("scripts\\img\\dlg_invite_event_progress_bar.png",
                                      confidence=.9,
                                      crop=Crop.UI_EVENT_DLG_PROGRESS):
                if not self.tvt_invite_dlg:
                    log('Found TvT invite dialog -> ignore it', bot=bot)
                    self.tvt_invite_dlg = True
                return True
            else:
                # Disconnect dialog (single button in dialog)
                top_left = l2window.locate_center("scripts\\img\\btn_top_left.png",
                                                  confidence=.9,
                                                  crop=Crop.DIALOG_BTN_1_TOP_LEFT)
                bottom_right = l2window.locate_center("scripts\\img\\btn_bottom_right.png",
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_BTN_1_BOTTOM_RIGHT)
                if top_left and bottom_right:
                    log('Disconnected dialog -> Ok', bot=bot)
                    l2window.activate()
                    (tlx, tly) = top_left
                    (brx, bry) = bottom_right

                    x = tlx + (brx - tlx) / 2
                    y = tly + (bry - tly) / 2
                    Mouse.double_click(x, y)
                    self.maybe_disconnected = True
                    self.just_resurrected = True
                    time.sleep(1)
                    Mouse.move_to(x, y - 100)
                    return True

                # Resurrection confirm dialog
                top_left = l2window.locate_center("scripts\\img\\btn_top_left.png",
                                                  confidence=.9,
                                                  crop=Crop.DIALOG_BTN_2_TOP_LEFT)
                bottom_right = l2window.locate_center("scripts\\img\\btn_bottom_right.png",
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_BTN_2_BOTTOM_RIGHT)
                if top_left and bottom_right:

                    if not self.res_delay_timer.is_started():
                        log('Found res confirm dialog', bot=bot)
                        self.res_delay_timer.start()

                    if self.res_delay_timer.is_ended():
                        log('Resurrection confirm dialog -> Accept', bot=bot)
                        l2window.activate()
                        (tlx, tly) = top_left
                        (brx, bry) = bottom_right

                        x = tlx + (brx - tlx) / 2
                        y = tly + (bry - tly) / 2
                        Mouse.double_click(x, y)
                        self.just_resurrected = True
                        self.expect_tp = True
                        self.state = 0
                    return True

        self.tvt_invite_dlg = False     # Reset tvt invite flag

        # Resurrection exclamation mark
        exclamation_pos = l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                                 confidence=.9,
                                                 crop=Crop.DIALOG_RESURRECTION_EXCLAMATION_MARK)

        # Confirm Resurrection dialog
        if exclamation_pos:
            icon_confirm_pos = l2window.locate_center(["scripts\\auto_farm\\img\\icon_l_coin_confirm.png",
                                                       "scripts\\auto_farm\\img\\icon_adena_confirm.png",
                                                       "scripts\\auto_farm\\img\\eigis\\icon_res_coin_confirm.png"],
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_RESURRECTION_COIN)

            if not self.res_delay_timer.is_started():
                log('Found confirm dialog', bot=bot)
                self.res_delay_timer.start()

            if self.res_delay_timer.is_ended():
                if icon_confirm_pos:
                    l2window.activate()
                    log("Resurrect confirm for L-coin or Res-coin (eigis)", bot=bot)
                    (x, y) = icon_confirm_pos
                    x += 110
                    y += 45
                    Mouse.double_click(x, y)
                else:
                    log("Resurrect free confirm", bot=bot)
                    (x, y) = exclamation_pos
                    x += 110
                    y += 85
                    Mouse.double_click(x, y)

                self.just_resurrected = True
                self.expect_tp = True
                self.res_delay_timer.reset()
                self.state = 0
                return True
            return False

        # Resurrection dialog
        else:
            if l2window.double_click_on_image(["scripts\\auto_farm\\img\\assassin\\icon_l_coin_resurrect.png",
                                               "scripts\\auto_farm\\img\\eigis\\icon_res_coin_resurrect.png"],
                                              confidence=.9,
                                              crop=Crop.DIALOG_RESURRECT):
                log('Resurrect for L-coins (assassin) or Res-coins (eigis)', bot=bot)
                self.state = 2
                return True
            else:
                gear_pos = l2window.locate_center("scripts\\auto_farm\\img\\icon_gear_resurrect.png",
                                                  confidence=.9,
                                                  crop=Crop.DIALOG_RESURRECT)
                if gear_pos:
                    log('Resurrect for free (assassin)', bot=bot)
                    l2window.activate()
                    (x, y) = gear_pos
                    (cx, cy) = l2window.window_center()
                    delta_y = cy - y
                    y = cy + delta_y / 3
                    x = cx
                    Mouse.double_click(x, y)
                    return True
        return False

    def run(self, l2window: L2Window, bot: L2Bot) -> bool:

        # next_tp_icon = self.custom_tp.next_tp()
        # if self.game.tp_to_spot(next_tp_icon):
        #     pass
        # return True

        auto_farm = self.game.auto_farm
        just_resurrected, self.just_resurrected = self.just_resurrected, False

        # Script was terminated - do nothing
        if self.state == STOP_SCRIPT:
            return True

        if self.game.tp_in_progress:
            if not self.expect_tp:
                log("Unexpected teleportation detected (1) -> stop script", bot=bot)
                self.game.tp_reset()
                self.state = STOP_SCRIPT
                return True

        if self.game.tp_done:
            if self.expect_tp:
                log("Teleportation done", bot=bot)
                self.just_teleported = True
                self.expect_tp = False
            else:
                log("Unexpected teleportation detected (2) -> stop script", bot=bot)
                self.state = STOP_SCRIPT
                return True

        if just_resurrected:
            log("Just resurrected", bot=bot)

        # Do nothing if script is not enabled
        if not bot.active:
            # stop auto farm
            if auto_farm:
                l2window.activate()
                Keyboard.input(b'<esc><alt+z>')
            self.game.tp_reset()
            return True

        # Reset UI
        if not self._ui_reset and not auto_farm:
            l2window.activate()
            log('Reset UI', bot=bot)
            # reset UI to ensure everything is visible
            Keyboard.input(b'<alt+l>')
            # close login rewards dialog
            l2window.close_all_dialogs()
            self._ui_reset = True

        # Check if welcome dialog is on screen - close it
        if self.game.is_welcome_dialog():
            log('Found welcome dialog -> close it', bot=bot)
            l2window.activate()
            l2window.close_all_dialogs()

        # Find and process dialogs
        if self.handle_l2_dialog(l2window, bot=bot):
            return True

        if self.instance_zone_farm.is_instance_zone(l2window):
            result = self.instance_zone_farm.handle(l2window,
                                                    bot,
                                                    auto_farm=auto_farm,
                                                    just_teleported=self.just_teleported,
                                                    just_resurrected=just_resurrected)
            self.expect_tp = self.instance_zone_farm.expect_tp
            return result

        # if in town
        if self.state == 0:
            if auto_farm:
                log('Currently farming (auto-farm) -> do nothing, so far', bot=bot)
                self.state = 2
                return True

            if not self.tp_delay_timer.is_started():
                log('In town -> delay before teleportation to spot', bot=bot)
                self.tp_delay_timer.start()
                return True

            if self.tp_delay_timer.is_ended():
                log('Delay ended -> teleport to spot', bot=bot)
                if auto_farm:
                    l2window.activate()
                    Keyboard.input(b'<esc><alt+z>')

                next_tp_icon = self.custom_tp.next_tp()
                if self.game.tp_to_spot(next_tp_icon):
                    self.tp_delay_timer.reset()
                    self.tp_done_timer.start()
                    self.expect_tp = True
                    self.state = 1

        # wait for teleport to spot
        if self.state == 1:
            if self.game.tp_in_progress and self.tp_done_timer.is_running():
                self.tp_done_timer.reset()

            if self.just_teleported:
                self.tp_done_timer.reset()
                delay = self.autofarm_delay_timer.max

                if not self.autofarm_delay_timer.is_started() and delay > 0:
                    log('Teleported to spot -> delay before start auto-farm', bot=bot)
                    self.autofarm_delay_timer.start()
                    return True

                if self.autofarm_delay_timer.is_ended() or delay == 0:
                    log('Teleported to spot -> start auto-farm', bot=bot)
                    # start auto-farm
                    l2window.activate()

                    # Keyboard.input(b'<alt+z>')
                    if l2window.click_on_image([
                        "scripts\\auto_farm\\img\\assassin\\autofarm_off.png",
                        "scripts\\auto_farm\\img\\deathknight2\\autofarm_off.png",
                        "scripts\\auto_farm\\img\\innadril\\autofarm_off.png"
                    ], confidence=.9, attempts=3, move_cursor=True):
                        self.just_teleported = False
                        self.expect_tp = False
                        self.state = 2
                        if self.game.auto_farm:
                            self.autofarm_delay_timer.reset()
                            return True

                    log('Unable to start auto-farm, try again', bot=bot)
                    return True
            else:
                if self.tp_done_timer.is_ended():
                    log('Teleportation failed. (no teleport scroll or teleportation forbidden) -> stop script',
                        bot=bot)
                    self.tp_done_timer.reset()
                    self.expect_tp = False
                    self.state = 99
                    return False
            return False

        # Currently farming
        if self.state == 2:
            # Probably admin or player disabled auto-farm
            # if not auto_farm:
            #     log("Player or admin disabled auto-farm -> stop script", bot=bot)
            #     self.state = 99
            #     return True

            # Probably dead and resurrected in town
            if self.just_teleported:
                self.state = 0
                self.just_teleported = False
                return False
        return True

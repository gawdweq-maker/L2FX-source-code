import time

from kbdmou import Mouse
from scripts import L2Window, L2Bot
from scripts.copper import Crop
from scripts.utils import log


class InstanceZoneFarm:

    def __init__(self):
        self.state = 0
        self.expect_tp = False

    def is_instance_zone(self, l2window: L2Window) -> bool:
        return l2window.locate_center('scripts\\auto_farm\\img\\instance_clock_right.png',
                                      confidence=.9,
                                      crop=[Crop.UI_INSTANCE_CLOCK_1,
                                            Crop.UI_INSTANCE_CLOCK_2])

    def exit_instance_zone(self, l2window: L2Window, bot: L2Bot) -> bool:
        # Is the instance - exit!
        instance_icon = l2window.locate_center('scripts\\auto_farm\\img\\instance_clock_right.png',
                                               confidence=.9,
                                               crop=[Crop.UI_INSTANCE_CLOCK_1,
                                                     Crop.UI_INSTANCE_CLOCK_2])
        if instance_icon:
            log('In instance -> exit', bot=bot)
            x, y = instance_icon
            y = y + 50
            Mouse.double_click(x, y)
            time.sleep(.5)
            y = y + 150
            Mouse.move_to(x, y)

            # Disconnect and Invite dialog exclamation mark
            if l2window.locate_center("scripts\\img\\icon_exclamation_mark.png",
                                      confidence=.9,
                                      attempts=10,
                                      crop=Crop.DIALOG_DISCONNECT_EXCLAMATION_MARK):

                # Resurrection confirm dialog
                top_left = l2window.locate_center("scripts\\img\\btn_top_left.png",
                                                  confidence=.9,
                                                  crop=Crop.DIALOG_BTN_2_TOP_LEFT)
                bottom_right = l2window.locate_center("scripts\\img\\btn_bottom_right.png",
                                                      confidence=.9,
                                                      crop=Crop.DIALOG_BTN_2_BOTTOM_RIGHT)
                if top_left and bottom_right:
                    log('Leave instance zone dialog -> OK', bot=bot)
                    (tlx, tly) = top_left
                    (brx, bry) = bottom_right

                    x = tlx + (brx - tlx) / 2
                    y = tly + (bry - tly) / 2
                    Mouse.click(x, y)

                    if l2window.locate_center('scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_bl.png',
                                              confidence=.9,
                                              attempts=10,
                                              crop=Crop.UI_INSTANCE_RESULTS_BOTTOM_LEFT) or \
                       l2window.locate_center('scripts\\auto_login\\img\\deathknight2\\welcome_dlg_decor_br.png',
                                              confidence=.9,
                                              attempts=10,
                                              crop=Crop.UI_INSTANCE_RESULTS_BOTTOM_RIGHT):
                        log('Found instance results dialog -> close it', bot=bot)
                        l2window.close_all_dialogs()

                    self.expect_tp = True
                    self.state = 0
                return True

    def handle(self, l2window: L2Window,
               bot: L2Bot, auto_farm: bool,
               just_teleported: bool, just_resurrected: bool) -> bool:

        if self.state == 0:
            if auto_farm:
                # Farming - switch to state 1
                log('Auto-farm in instance -> do nothing')
                self.state = 1
                return True
            else:
                # Not farming - return to the town
                return self.exit_instance_zone(l2window, bot)

        elif self.state == 1:
            if just_resurrected:
                # Just resurrected after farming - exist instance
                return self.exit_instance_zone(l2window, bot)
        return True

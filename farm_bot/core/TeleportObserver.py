import l2helper
from scripts import L2Window
from scripts.copper import Crop


class TeleportObserver:

    def __init__(self, l2window: L2Window):
        self.is_black_screen = False
        self.tp_done = False
        self.tp_in_progress = False
        self.l2window = l2window

    def find_black(self, screenshot, crop=None) -> bool:
        if not screenshot:
            return False
        if crop:
            img_box = crop.value.crop(screenshot)
        else:
            img_box = screenshot

        image_bytes = img_box.tobytes()
        average = sum(image_bytes) / len(image_bytes)
        # print(average)
        return 0.0 < average < 5.0

    def is_tp(self):
        screenshot = l2helper.capture_window_observer(self.l2window.hwnd)
        weight = 0
        if self.find_black(screenshot, crop=Crop.TP_DETECT_0):
            weight = weight + 1
        if self.find_black(screenshot, crop=Crop.TP_DETECT_1):
            weight = weight + 1
        if weight >= 2:
            return True
        if self.find_black(screenshot, crop=Crop.TP_DETECT_2):
            weight = weight + 1
        if weight >= 2:
            return True
        if self.find_black(screenshot, crop=Crop.TP_DETECT_3):
            weight = weight + 1
        return weight >= 2

    def is_tp_done(self) -> bool:
        prev_teleport = True if self.is_black_screen else False
        self.is_black_screen = self.is_tp()
        if self.is_black_screen:
            self.tp_in_progress = True
        if prev_teleport and not self.is_black_screen:
            self.tp_in_progress = False
            return True
        return False

    def get_and_reset_tp_done(self) -> bool:
        value = self.tp_done
        self.tp_done = False
        return value

    def update(self):
        if not self.tp_done:
            self.tp_done = self.is_tp_done()

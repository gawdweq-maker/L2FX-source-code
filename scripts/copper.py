import enum
from ctypes.wintypes import HWND

from PIL import Image

import l2helper


class Anchor(enum.Enum):
    CENTER = 'center'
    N = 'n'
    S = 's'
    W = 'w'
    E = 'e'
    NW = 'nw'
    SW = 'sw'
    NE = 'ne'
    SE = 'se'
    PERCENT = 'p'


class Cropper:
    __delta_x: float
    __delta_y: float
    __width: int
    __height: int
    __anchor: Anchor

    def __init__(self, width: int, height: int, anchor=Anchor.CENTER, delta_x=0.0, delta_y=0.0):
        self.__delta_x = delta_x
        self.__delta_y = delta_y
        self.__width = width
        self.__height = height
        self.__anchor = anchor

    def crop(self, img: Image) -> Image:

        crop_width = self.__width
        crop_height = self.__height

        if crop_width > img.width:
            crop_width = img.width
        if crop_height > img.height:
            crop_height = img.height

        if self.__anchor == Anchor.PERCENT:
            left = img.width * self.__delta_x - crop_width/2
            top = img.height * self.__delta_y - crop_height / 2
            right = img.width * self.__delta_x + crop_width/2
            bottom = img.height * self.__delta_y + crop_height / 2
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.CENTER:
            left = (img.width - crop_width)/2 + self.__delta_x
            top = (img.height - crop_height)/2 + self.__delta_y
            right = (img.width + crop_width)/2 + self.__delta_x
            bottom = (img.height + crop_height)/2 + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.N:
            left = (img.width - crop_width)/2 + self.__delta_x
            top = 0 + self.__delta_y
            right = (img.width + crop_width)/2 + self.__delta_x
            bottom = crop_height + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.S:
            left = (img.width - crop_width)/2 + self.__delta_x
            top = img.height - crop_height + self.__delta_y
            right = (img.width + crop_width)/2 + self.__delta_x
            bottom = img.height + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.W:
            left = 0 + self.__delta_x
            top = (img.height - crop_height)/2 + self.__delta_y
            right = crop_width + self.__delta_x
            bottom = (img.height + crop_height)/2 + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.E:
            left = img.width - crop_width + self.__delta_x
            top = (img.height - crop_height)/2 + self.__delta_y
            right = img.width + self.__delta_x
            bottom = (img.height + crop_height)/2 + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.NW:
            left = 0 + self.__delta_x
            top = 0 + self.__delta_y
            right = crop_width + self.__delta_x
            bottom = crop_height + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.SW:
            left = 0 + self.__delta_x
            top = img.height - crop_height + self.__delta_y
            right = crop_width + self.__delta_x
            bottom = img.height + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.NE:
            left = img.width - crop_width + self.__delta_x
            top = 0 + self.__delta_y
            right = img.width + self.__delta_x
            bottom = crop_height + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result
        elif self.__anchor == Anchor.SE:
            left = img.width - crop_width + self.__delta_x
            top = img.height - crop_height + self.__delta_y
            right = img.width + self.__delta_x
            bottom = img.height + self.__delta_y
            result = img.crop((left, top, right, bottom))
            result.top = top
            result.left = left
            return result

    def center_in_window(self, hwnd: HWND):
        wnd = l2helper.client_to_screen(hwnd)
        (width, height) = l2helper.client_size(hwnd)
        (btn_x, btn_y) = self.center(width, height)
        if hwnd:
            btn_x = wnd[0] + btn_x
            btn_y = wnd[1] + btn_y
        return btn_x, btn_y

    def center(self, width, height):
        if self.__anchor == Anchor.PERCENT:
            return width * self.__delta_x, height * self.__delta_y
        elif self.__anchor == Anchor.CENTER:
            return width/2 + self.__delta_x, height/2 + self.__delta_y
        elif self.__anchor == Anchor.N:
            return width/2 + self.__delta_x, 0 + self.__delta_y + self.__height/2
        elif self.__anchor == Anchor.S:
            return width/2 + self.__delta_x, height + self.__delta_y - self.__height/2
        elif self.__anchor == Anchor.W:
            return 0 + self.__delta_x + self.__width/2, height/2 + self.__delta_y
        elif self.__anchor == Anchor.E:
            return width + self.__delta_x - self.__width/2, height/2 + self.__delta_y
        elif self.__anchor == Anchor.NW:
            return 0 + self.__delta_x + self.__width/2, 0 + self.__delta_y + self.__height/2
        elif self.__anchor == Anchor.SW:
            return 0 + self.__delta_x + self.__width/2, height + self.__delta_y - self.__height/2
        elif self.__anchor == Anchor.NE:
            return width + self.__delta_x - self.__width/2, 0 + self.__delta_y + self.__height/2
        elif self.__anchor == Anchor.SE:
            return width + self.__delta_x - self.__width/2, height + self.__delta_y - self.__height/2


class Crop(enum.Enum):
    LOGIN_PASS = Cropper(400, 150, anchor=Anchor.PERCENT, delta_x=.5, delta_y=.58)
    LOGIN_LICENSE = Cropper(290, 50, delta_y=220)
    LOGIN_SERVER_SELECT_CRUSADER_TOP_RIGHT_CORNER = Cropper(50, 50, anchor=Anchor.NE, delta_y=30)
    LOGIN_SERVER_SELECT_BTN_ASSASSIN = Cropper(30, 50, anchor=Anchor.S, delta_x=-290, delta_y=-220)
    LOGIN_SERVER_SELECT_BTN_CANCEL = Cropper(120, 30, anchor=Anchor.S, delta_x=66, delta_y=-175)
    LOGIN_SERVER_SELECT_BTNS = Cropper(40, 350, anchor=Anchor.S)
    LOGIN_CHAR_SELECT = Cropper(120, 40, anchor=Anchor.S)
    LOGIN_CHAR_SELECT_BTN_LEFT = Cropper(18, 38, anchor=Anchor.S, delta_x=-50)
    LOGIN_BIG_DIALOG = Cropper(90, 40, anchor=Anchor.CENTER, delta_y=85)
    LOGIN_CONNECTION_IN_PROGRESS_BNT = Cropper(110, 20, delta_y=15)
    DIALOG_NORMAL = Cropper(320, 140)
    DIALOG_BIG = Cropper(380, 230)
    DIALOG_RESURRECT = Cropper(200, 230)
    DIALOG_RESURRECT_QUESTION = Cropper(20, 100, delta_x=-73, delta_y=0)
    DIALOG_RESURRECT_GEAR = Cropper(24, 94, delta_x=84, delta_y=-98)
    DIALOG_RESURRECT_GEAR_1 = Cropper(20, 20, delta_x=82, delta_y=-87)
    DIALOG_RESURRECT_GEAR_2 = Cropper(20, 20, delta_x=82, delta_y=-102)
    DIALOG_RESURRECT_GEAR_3 = Cropper(20, 20, delta_x=82, delta_y=-117)
    DIALOG_RESURRECT_GEAR_4 = Cropper(20, 20, delta_x=82, delta_y=-132)
    DIALOG_RESURRECT_L_COIN_BTN = Cropper(165, 25, delta_y=27)
    DIALOG_RESURRECT_OK_BTN = Cropper(117, 33, delta_x=-60, delta_y=81)
    DIALOG_RESURRECT_TO_VILLAGE_BTN = Cropper(15, 28, delta_x=-80, delta_y=-58)
    DIALOG_RESURRECTION_EXCLAMATION_MARK = Cropper(38, 50, delta_x=-164, delta_y=-80)
    DIALOG_RESURRECTION_EXCLAMATION_MARK_2 = Cropper(30, 30, delta_y=-107)
    DIALOG_RESURRECTION_EXCLAMATION_MARK_3 = Cropper(38, 50, delta_x=-128, delta_y=-45)
    DIALOG_RESURRECTION_QUESTION_MARK_2 = Cropper(30, 30, delta_y=-25)
    DIALOG_RESURRECTION_QUESTION_MARK_3 = Cropper(30, 30, delta_y=-35)
    DIALOG_RESURRECTION_QUESTION_MARK_4 = Cropper(30, 30, delta_y=-82)
    DIALOG_RESURRECTION_COIN = Cropper(45, 70, delta_x=-157, delta_y=35)
    DIALOG_RESURRECTION_COIN_2 = Cropper(40, 40, delta_x=-156, delta_y=24)
    DIALOG_DISCONNECT_EXCLAMATION_MARK = Cropper(38, 38, delta_x=-128, delta_y=-40)
    DIALOG_DISCONNECT_EXCLAMATION_MARK_2 = Cropper(30, 30, delta_y=-90)
    DIALOG_PARTY_INVITE_EXCLAMATION_MARK = Cropper(38, 38, delta_x=360, delta_y=-92, anchor=Anchor.SW)
    DIALOG_PARTY_INVITE_QUESTION_MARK_2 = Cropper(30, 30, delta_x=523, delta_y=-168, anchor=Anchor.SW)
    DIALOG_SKELTH_TELEPORT_QUESTION_MARK = Cropper(30, 30, delta_y=-92)

    UI_EXP = Cropper(36, 30, anchor=Anchor.SW)
    UI_MAP_WAYPOINT = Cropper(30, 30, anchor=Anchor.NE, delta_x=-175)
    UI_MENU = Cropper(60, 80, anchor=Anchor.SE, delta_x=0)
    # UI_MY_TELEPORT_BTN = Cropper(40, 40, anchor=Anchor.NE, delta_y=170)

    UI_MY_TELEPORT = Cropper(250, 350)
    UI_MY_TELEPORT_ADD_CUSTOM_TP = Cropper(50, 50, delta_x=-100, delta_y=145)
    UI_AUTO_FARM = Cropper(750, 200, anchor=Anchor.SE)
    UI_AUTO_FARM_L2PLAYERS = Cropper(1000, 70, delta_y=-85, delta_x=-85, anchor=Anchor.SE)
    UI_WELCOME_DECOR_LEFT = Cropper(50, 50, delta_x=-460, delta_y=-160)
    UI_WELCOME_DECOR_RIGHT = Cropper(50, 50, delta_x=460, delta_y=-160)
    UI_BUFFS = Cropper(400, 102, delta_y=100, delta_x=0, anchor=Anchor.NW)

    UI_EVENT_DLG_PROGRESS = Cropper(20, 20, delta_x=-130, delta_y=15)

    UI_MAP = Cropper(320, 320, anchor=Anchor.W, delta_x=20, delta_y=0)
    UI_MAP_MY_TELEPORT_BTN = Cropper(40, 55, anchor=Anchor.W, delta_x=195, delta_y=153)

    UI_REWARDS_LOCK = Cropper(45, 55, delta_x=263, delta_y=167)
    UI_CLOSE_BALTUS_BTN = Cropper(24, 24, anchor=Anchor.NE, delta_x=-220, delta_y=55)
    UI_INSTANCE_CLOCK_AREA = Cropper(260, 100, anchor=Anchor.NE, delta_x=-217, delta_y=8)
    UI_INSTANCE_CLOCK_1 = Cropper(52, 52, anchor=Anchor.NE, delta_x=-227, delta_y=8)
    UI_INSTANCE_CLOCK_2 = Cropper(52, 52, anchor=Anchor.NE, delta_x=-314, delta_y=8)
    UI_INSTANCE_RESULTS_LEFT = Cropper(50, 70, delta_x=-120, delta_y=-70)
    UI_INSTANCE_RESULTS_RIGHT = Cropper(50, 70, delta_x=120, delta_y=-70)
    UI_INSTANCE_RESULTS_BOTTOM_LEFT = Cropper(30, 30, delta_x=-125, delta_y=60)
    UI_INSTANCE_RESULTS_BOTTOM_RIGHT = Cropper(30, 30, delta_x=125, delta_y=60)

    UI_BTN_USE_OF_TOKEN = Cropper(44, 44, anchor=Anchor.W, delta_x=103, delta_y=6)
    UI_BTN_MY_TELEPORT = Cropper(45, 45, anchor=Anchor.W, delta_x=173, delta_y=-223)

    DIALOG_BTN_1_TOP_LEFT = Cropper(20, 10, delta_x=-30, delta_y=38)
    DIALOG_BTN_1_BOTTOM_RIGHT = Cropper(20, 10, delta_x=33, delta_y=56)

    DIALOG_BTN_2_TOP_LEFT = Cropper(20, 10, delta_x=-73, delta_y=38)
    DIALOG_BTN_2_BOTTOM_RIGHT = Cropper(20, 10, delta_x=-12, delta_y=56)

    DIALOG_BTN_3_TOP_LEFT = Cropper(20, 10, delta_x=13, delta_y=38)
    DIALOG_BTN_3_BOTTOM_RIGHT = Cropper(20, 10, delta_x=72, delta_y=56)

    TP_DETECT_0 = Cropper(16, 16, anchor=Anchor.NW, delta_y=1, delta_x=1)
    TP_DETECT_1 = Cropper(16, 16, anchor=Anchor.NE, delta_y=105, delta_x=-215)
    TP_DETECT_2 = Cropper(16, 16, anchor=Anchor.NW, delta_y=115, delta_x=5)
    TP_DETECT_3 = Cropper(16, 16, anchor=Anchor.SW, delta_y=-8, delta_x=30)

    # VALHALLA_DARK = Cropper(40, 40, delta_y=-35, delta_x=-225)
    # VALHALLA_LIGHT = Cropper(40, 40, delta_y=-35, delta_x=170)

    VALHALLA_ASGARD = Cropper(40, 40, delta_y=-35, delta_x=-225)
    VALHALLA_MIDGARD = Cropper(40, 40, delta_y=-35, delta_x=-25)
    VALHALLA_SUNRISE = Cropper(40, 40, delta_y=-35, delta_x=175)

    VALHALLA_PIN_PAD = Cropper(150, 170, delta_y=-30, delta_x=180)
    VALHALLA_PIN_PAD_CLEAR = Cropper(60, 60, delta_y=35, delta_x=205)

    VALHALLA_ONLINE_REWARD_BOX = Cropper(55, 65, delta_x=-245, delta_y=210, anchor=Anchor.NE)


import PIL
from PIL import ImageTk
from PIL.Image import Image


class Item:
    __icon: Image
    __icon_tk: ImageTk.PhotoImage
    __name: str

    def __init__(self, icon_file: str, name: str):
        self.__icon = PIL.Image.open(icon_file)
        self.__icon_tk = None
        self.__name = name

    @property
    def icon(self) -> Image:
        return self.__icon

    @property
    def name(self) -> str:
        return self.__name

    @property
    def icon_tk(self) -> ImageTk:
        if self.__icon_tk is None:
            self.__icon_tk = ImageTk.PhotoImage(self.icon)
        return self.__icon_tk


SAYHA_BLESSING = Item("scripts\\auto_purchase\\items\\sayha's_blessing.png", "Благословение Сайхи")
SOUL_SHOT = Item("scripts\\auto_purchase\\items\\soulshot.png", "Купон на заряды душ")
SCROLL_BOOST_ATTACK = Item("scripts\\auto_purchase\\items\\scroll_boost_attack.png", "Свиток: Модифицировать Атаку")
SCROLL_BOOST_DEFENSE = Item("scripts\\auto_purchase\\items\\scroll_boost_defense.png", "Свиток: Модифицировать Защиту")
XP_GROWTH_SCROLL = Item("scripts\\auto_purchase\\items\\xp_growth_scroll.png", "Свиток Увеличения Опыта")
SAYHA_STORM_LV3 = Item("scripts\\auto_purchase\\items\\sayha's_storm_lv3.png", "Шторм Сайхи Ур. 3")
MY_TELEPORT_SCROLL = Item("scripts\\auto_purchase\\items\\my_teleport_scroll.png", "Свиток Свободного Телепорта")

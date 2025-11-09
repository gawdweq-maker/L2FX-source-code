from abc import ABC, abstractmethod
from typing import Tuple


class L2Window(ABC):
    @property
    @abstractmethod
    def hwnd(self):
        pass

    @property
    @abstractmethod
    def screenshot(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass

    @abstractmethod
    def is_active(self) -> bool:
        pass

    @abstractmethod
    def switch_keyboard_to_english(self):
        pass

    @abstractmethod
    def window_center(self) -> Tuple[int, int] or None:
        pass

    @abstractmethod
    def window_size(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def client_to_screen(self) -> Tuple[int, int]:
        pass

    @abstractmethod
    def locate_center(self, img, confidence=1, attempts=1, crop=None):
        pass

    @abstractmethod
    def click_on_image(self, img, confidence=1, attempts=1, crop=None, move_cursor=False) -> bool:
        pass

    @abstractmethod
    def double_click_on_image(self, img, confidence=1, attempts=1, crop=None, move_cursor=False) -> bool:
        pass

    @abstractmethod
    def mouse_move_on_image(self, img, confidence=1, attempts=1, crop=None) -> bool:
        pass

    @abstractmethod
    def mouse_click(self, pos: Tuple[int, int]):
        pass

    @abstractmethod
    def mouse_double_click(self, pos: Tuple[int, int]):
        pass

    @abstractmethod
    def dump_screen(self, file_name: str, crop=None):
        pass

    @property
    def is_valhalla(self) -> bool:
        pass
        return False

    @property
    def is_l2players(self) -> bool:
        pass
        return False

    @property
    def is_l2skelth(self) -> bool:
        pass
        return False

    @abstractmethod
    def close_all_dialogs(self):
        pass

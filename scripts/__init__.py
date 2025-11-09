from abc import ABC, abstractmethod
from tkinter import Frame

from farm_bot.core.L2Bot import L2Bot
from farm_bot.core.L2Window import L2Window
from scripts import Properties
from scripts.Properties import Settings


class L2Script(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def run(self, l2window: L2Window, bot: L2Bot) -> bool:
        pass

    @abstractmethod
    def on_account_changed(self, account: Properties.Account):
        pass


class FrameComponent(Frame, ABC):
    @abstractmethod
    def on_update_settings(self, settings: Settings):
        pass

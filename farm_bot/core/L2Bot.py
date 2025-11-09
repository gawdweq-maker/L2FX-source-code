from abc import ABC, abstractmethod


class L2Bot(ABC):
    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def set_refresh_interval(self, interval: int):
        pass

    @property
    @abstractmethod
    def active(self) -> bool:
        pass

    @abstractmethod
    def enabled(self) -> bool:
        pass

    @abstractmethod
    def tab_id(self) -> str:
        pass

    @abstractmethod
    def cuid(self) -> int:
        pass

    @abstractmethod
    def stop(self):
        pass

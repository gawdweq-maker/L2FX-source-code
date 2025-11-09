from datetime import datetime

from view.delay_entry import DelayEntry


class DelayTimer:

    __delay_entry: DelayEntry

    def __init__(self, delay_entry: DelayEntry):
        self.__start_time = None
        self.__count_seconds = None
        self.__delay_seconds = None
        self.__delay_entry = delay_entry
        self.__is_started = False

    def start(self):
        self.__start_time = datetime.utcnow()
        self.__delay_seconds = self.__delay_entry.get()  # pick random value
        self.__is_started = True

    def reset(self):
        self.__start_time = None
        self.__count_seconds = None
        self.__is_started = False

    @property
    def max(self) -> int:
        return self.__delay_seconds or 0

    @property
    def count(self) -> int:
        if self.__start_time is not None:
            self.__count_seconds = int((datetime.utcnow() - self.__start_time).total_seconds())
        return self.__count_seconds

    def is_started(self) -> bool:
        return self.__is_started

    def is_ended(self) -> bool:
        return self.count is not None and self.__delay_seconds is not None and self.count >= self.__delay_seconds

    def is_running(self) -> bool:
        return self.is_started() and not self.is_ended()

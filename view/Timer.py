from datetime import datetime


class Timer:
    def __init__(self, seconds: int):
        self.__start_time = None
        self.__count_seconds = 0
        self.__delay_seconds = seconds

    def start(self):
        self.__start_time = datetime.utcnow()

    def reset(self):
        self.__start_time = None
        self.__count_seconds = 0

    @property
    def count(self) -> int:
        if self.__start_time is not None:
            self.__count_seconds = int((datetime.utcnow() - self.__start_time).total_seconds())
        return self.__count_seconds

    def is_started(self) -> bool:
        count = self.count
        return count is not None and count > 0

    def is_ended(self) -> bool:
        count = self.count
        return count is not None and self.__delay_seconds is not None and count >= self.__delay_seconds

    def is_running(self) -> bool:
        return self.is_started() and not self.is_ended()



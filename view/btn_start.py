import enum
from tkinter import Button, LEFT
from PIL import ImageTk

from view.ui import Icons


class StartStopButton(Button):

    class State(enum.Enum):
        START = 0
        STOP = 1

    __state: State
    __play_icon: ImageTk
    __stop_icon: ImageTk

    def next_state(self):
        if self.__state == self.State.START:
            self.__state = self.State.STOP
            if self.__command_start:
                self.__command_start()
        elif self.__state == self.State.STOP:
            self.__state = self.State.START
            if self.__command_stop:
                self.__command_stop()
        self.__update_state()

    def stop(self):
        if self.__state == self.State.STOP:
            self.__state = self.State.START
            if self.__command_stop:
                self.__command_stop()
            self.__update_state()

    def __update_state(self):
        if self.__state == self.State.START:
            self.configure(text=" Start", image=self.__play_icon)
        elif self.__state == self.State.STOP:
            self.configure(text=" Stop", image=self.__stop_icon)

    @property
    def state(self):
        return self.__state

    def __init__(self, master, command_start=None, command_stop=None):
        self.__play_icon = Icons.play
        self.__stop_icon = Icons.stop
        self.__state = self.State.START
        self.__command_start = command_start
        self.__command_stop = command_stop
        super().__init__(master, compound=LEFT, command=self.next_state)
        self.__update_state()

import random
from functools import partial
from tkinter import Frame, Button, NW, Tk, DISABLED, NORMAL, Misc
from typing import List

from PIL import Image, ImageTk
import PIL

from scripts import L2Script, L2Window, L2Bot, Properties
from view.ModalDialog import ModalDialog

PROPERTY_NAME = 'custom_tp_list'
TP_PER_LINE = 6
MAX_TELEPORTS = 24


class CustomTpIcon:

    icon: PIL.Image
    img_tk: ImageTk

    def __init__(self, file_name):
        self.icon = PIL.Image.open(file_name)
        self.img_tk = ImageTk.PhotoImage(self.icon)


class SelectCustomTpDialog(ModalDialog):

    _icons_tp: List[CustomTpIcon]
    _selected = None

    def __init__(self, parent: Tk, icons_tp: List[CustomTpIcon]):
        super().__init__(parent)
        self._icons_tp = icons_tp

        self.geometry('265x227')
        self.title("Choose custom TP spot for farm")
        self.wm_attributes('-toolwindow', 1)
        self.resizable(width=False, height=False)

        for i in range(0, 42):
            btn = Button(self, image=self._icons_tp[i].img_tk, command=partial(self._on_select, i))
            btn.grid(row=i // 7, column=i % 7)

    def _on_select(self, index):
        self._selected = index
        self.close_dialog()

    @property
    def selected(self):
        return self._selected


class CustomTp(L2Script, Frame):

    _props: Frame
    _icons: List[CustomTpIcon] = list()
    _current_tp = -1
    _btn_plus = None
    _root: Tk

    def __init__(self, master: Misc, root: Tk):
        super().__init__(master)
        self._root = root
        self._btns = []
        self.account = None
        icon_file = "scripts\\custom_tp\\img\\btn_add.png"
        self.__icon_plus = ImageTk.PhotoImage(PIL.Image.open(icon_file))

        for i in range(0, 42):
            file_name = f'scripts\\custom_tp\\img\\icon_tp_{i}.png'
            self._icons.append(CustomTpIcon(file_name))

        self._props = Frame(master)
        self._btn_plus = Button(self._props, image=self.__icon_plus, command=self.open_dialog)
        self._btn_plus.grid(padx=3, pady=10, row=0, column=7)
        self._props.pack(padx=10, pady=(3, 8), anchor=NW)

    def update_grid(self, btn, pos):
        btn.grid(row=int(pos / TP_PER_LINE), column=pos % TP_PER_LINE)
        self._btn_plus.grid(padx=3, pady=10, row=int(pos / TP_PER_LINE), column=pos % TP_PER_LINE + 1)

    def on_account_changed(self, account: Properties.Account):
        self.account = account

        for btn in self._btns:
            btn.destroy()
        self._btns = []

        if account:
            for idx, tp in enumerate(self.account.custom_tp_list):
                btn = Button(self._props, image=self._icons[tp].img_tk,
                             command=partial(self.on_remove_farm_spot, idx))
                self.update_grid(btn, idx)
                self._btns.append(btn)

            if len(self.account.custom_tp_list) >= MAX_TELEPORTS:
                self._btn_plus.configure(state=DISABLED)

    def reset(self):
        pass

    def open_dialog(self):
        dlg = SelectCustomTpDialog(self._root, self._icons)
        self._root.wait_window(dlg)
        if dlg.selected is not None:
            self.account.custom_tp_list.append(dlg.selected)
            Properties.save_properties()
            pos = len(self.account.custom_tp_list) - 1
            btn = Button(self._props, image=self._icons[dlg.selected].img_tk, command=partial(self.on_remove_farm_spot, pos))
            self.update_grid(btn, pos)
            self._btns.append(btn)

        if len(self.account.custom_tp_list) >= MAX_TELEPORTS:
            self._btn_plus.configure(state=DISABLED)

    def on_remove_farm_spot(self, idx):
        self._btns[idx].destroy()
        del self._btns[idx]
        del self.account.custom_tp_list[idx]
        Properties.save_properties()

        pos = 0
        for btn in self._btns:
            btn.configure(command=partial(self.on_remove_farm_spot, pos))
            self.update_grid(btn, pos)
            pos += 1

        self._btn_plus.configure(state=NORMAL)

    def next_tp(self, random_pick: int) -> Image:
        if random_pick > 0:
            # Random
            num_of_tps = len(self.account.custom_tp_list)
            if num_of_tps == 0:
                return None
            if num_of_tps == 1:
                self._current_tp = 0
            elif self._current_tp is None:
                self._current_tp = random.randrange(num_of_tps)
            else:
                valid_indices = [i for i in range(num_of_tps) if i != self._current_tp]
                self._current_tp = random.choice(valid_indices)

            tp_id = self.account.custom_tp_list[self._current_tp]
            return self._icons[tp_id].icon

        else:
            # Round robbin
            self._current_tp += 1
            if self._current_tp >= len(self.account.custom_tp_list):
                self._current_tp = 0
            if self._current_tp < len(self.account.custom_tp_list):
                tp_id = self.account.custom_tp_list[self._current_tp]
                return self._icons[tp_id].icon

        return None


    def has_next_tp(self) -> bool:
        return self.account and len(self.account.custom_tp_list) > 0

    def run(self, l2window: L2Window, bot: L2Bot):
        pass

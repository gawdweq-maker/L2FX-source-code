from abc import ABC, abstractmethod
from tkinter import Frame, LabelFrame, NW, Button, RIGHT, DISABLED, StringVar, NORMAL, messagebox
from tkinter.ttk import Combobox

from farm_bot.core import L2Game
from scripts.Properties import AccountRepository, save_properties, Account
from view.ui import Icons


class AccountsController(Frame):
    class Listener(ABC):
        @abstractmethod
        def on_select_account(self, account: Account or None):
            pass

    def __init__(self, game: L2Game, account_repository: AccountRepository, account_listener: Listener):
        super().__init__(game)
        self.__profile_var = StringVar()

        self.account_repository = account_repository
        self.account = account_repository.get_last_account()
        self.idx = account_repository.get_last_account_idx()
        self.account_listener = account_listener
        self.game = game
        self.in_game = False

        groupbox_profile = LabelFrame(self, text="Profile")
        groupbox_profile.pack(fill="both", expand=False, padx=7, pady=(0, 5))

        props2 = Frame(groupbox_profile)
        props2.pack(padx=10, pady=(3, 7), fill='x', anchor=NW)

        self.btn_del_account = Button(props2, image=Icons.trash, command=self.on_del_account)
        self.btn_del_account.pack(side=RIGHT, padx=(5, 0))

        self.btn_new_account = Button(props2, image=Icons.plus, command=self.on_new_account)
        self.btn_new_account.pack(side=RIGHT, padx=(9, 0))

        self.profiles = Combobox(props2, textvariable=self.__profile_var, width=27)
        self.profiles.pack(pady=(5, 5))
        self.profiles.bind("<<ComboboxSelected>>", lambda e: self.on_select_account(self.profiles.current()))
        self.profiles.bind("<KeyRelease>", lambda e: self.on_account_name_changed(self.__profile_var.get()))

        profiles = account_repository.names

        if len(profiles) == 0:
            self.on_new_account()

        if len(profiles) == 0:
            self.profiles.configure(state=DISABLED)
            self.btn_del_account.configure(state=DISABLED)
        else:
            if self.account:
                self.__profile_var.set(self.account.name)
            self.profiles.configure(values=profiles)
            self.account_listener.on_select_account(self.account)

    def on_new_account(self):
        self.account = self.account_repository.create()
        self.account_repository.set_last_account(self.account)
        values = self.account_repository.names
        self.profiles.configure(values=values)
        self.idx = len(values)-1
        self.profiles.current(self.idx)    # select last added
        self.profiles.configure(state=NORMAL)
        self.btn_del_account.configure(state=NORMAL)
        self.on_select_account(self.idx)
        self.profiles.selection_range(0, len(self.__profile_var.get()))
        self.profiles.icursor(len(self.__profile_var.get()))
        self.profiles.focus_set()

    def on_del_account(self):
        if messagebox.askyesno(f'Delete profile', f'Are you sure you want to delete profile "{self.account.name}"?'):
            self.account_repository.delete(self.account)
            values = self.account_repository.names
            self.profiles.configure(values=values)
            if len(values) == 0:
                self.__profile_var.set('')
                self.profiles.configure(state=DISABLED)
                self.btn_del_account.configure(state=DISABLED)
                self.account_listener.on_select_account(None)
            else:
                if self.idx > 0:
                    self.idx = self.idx - 1
                if self.idx > -1:
                    self.profiles.current(self.idx)
                self.on_select_account(self.idx)

    def on_select_account(self, idx: int):
        if idx > -1:
            self.account = self.account_repository.find_by_id(idx)
            if self.account:
                self.idx = idx
                self.account_repository.set_last_account(self.account)
                self.account_listener.on_select_account(self.account)
                self.focus_set()    # ensure focus will not be on combobox after switch

    def on_account_name_changed(self, name: str):
        if self.idx > -1:
            self.account = self.account_repository.find_by_id(self.idx)
            if self.account:
                if self.account.name != name:
                    self.account.name = name
                    save_properties()
                    values = self.account_repository.names
                    self.profiles.configure(values=values)

    # def on_update_settings(self, settings: Settings):
    #     if settings.multi_profile is True:
    #         self.groupbox_profile.pack(fill="both", expand=False, padx=7, pady=(0, 5))
    #     else:
    #         self.groupbox_profile.forget()

    @property
    def size(self) -> int:
        return len(self.account_repository.names)

import json
from json import JSONDecodeError
from os import path

import config
import l2helper

FILE_NAME = 'properties.json'

global properties


class Properties(object):
    def __init__(self, **kwargs):
        self.version = 1
        self.settings = Settings()
        self.clients = {}

        ver = kwargs.get('version')

        # Properties v1
        if ver == 1:
            for key, value in kwargs.items():
                if key == 'settings':
                    self.settings = Settings(**value)
                elif key == 'clients':
                    self.clients = {k: AccountRepository(**v) for k, v in value.items()}
                else:
                    self.__dict__[key] = value
        # Properties v0
        elif not ver:
            self.clients = {k: AccountRepository(**v) for k, v in kwargs.items()}
        # Unknown or wrong property version
        else:
            l2helper.msg_box(f'ERROR: Incorrect or corrupted file "{FILE_NAME}"\r\nNew file with properties will be created.',
                             config.APP_NAME,
                             l2helper.MB_ICONERROR)
            print(f'ERROR: Incorrect or corrupted file "{FILE_NAME}". New file with properties will be created.')


class Settings(object):
    screen_capture_interval_ms: int

    def __init__(self, *args, **kwargs):
        self.screen_capture_interval_ms = 100
        self.timer_range_mode = False
        self.power_saving_mode = False
        self.multi_profile = False
        self.advanced_res_settings = False
        self.advanced_farm_settings = False
        self.unlocker_enabled = False
        self.auto_clicker_enabled = False
        for k, v in kwargs.items():
            self.__dict__[k] = v


class Account(object):
    def __init__(self, *args, **kwargs):
        self.name = self.create_new_name(kwargs)
        self.login = ''
        self.password = ''
        self.valhalla_pin = ''
        self.custom_tp_list = []
        self.tp_timer = 0
        self.autofarm_timer = 0
        self.death_timer = 0
        self.reconnect_timer = 0
        self.res_for_adena = 0
        self.res_to_clan_hall = 0
        self.party_invite = 0
        self.random_teleport = 0
        self.instant_res = 0
        self.anti_admin_protection = 0
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def create_new_name(self, args) -> str:
        if 'login' in args:
            login = args['login']
            if len(login) > 0:
                return f'<unnamed> - {login}'
        return '<new>'


class AccountRepository(object):

    last_idx = 0

    def __init__(self, accounts: list):
        self.accounts = [Account(**d) for d in accounts]

    def create(self) -> Account:
        account = Account()
        self.accounts.append(account)
        return account

    def update(self, account: Account) -> Account:
        save_properties()
        return account

    def delete(self, account: Account):
        if account in self.accounts:
            self.accounts.remove(account)

    @property
    def logins(self) -> list:
        return [a.login for a in self.accounts]

    @property
    def names(self) -> list:
        return [a.name for a in self.accounts]

    def get_last_account(self) -> Account or None:
        for a in self.accounts:
            if hasattr(a, 'default') and a.default is True:
                return a
        return None

    def get_last_account_idx(self) -> int:
        for idx, a in enumerate(self.accounts):
            if hasattr(a, 'default') and a.default is True:
                return idx
        else:
            return -1

    def set_last_account(self, account: Account):
        for a in self.accounts:
            if hasattr(a, 'default') and a != Account:
                delattr(a, 'default')
        account.default = True

    def remove_account(self, account: Account):
        if account in self.accounts:
            self.accounts.remove(account)

    def find_by_id(self, idx: int) -> Account or None:
        if idx < 0 or len(self.accounts) == 0:
            return None
        return self.accounts[idx]


def load_properties():
    global properties
    if path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, 'r') as j:
                properties_data = json.loads(j.read())
                properties = Properties(**properties_data)
        except JSONDecodeError:
            l2helper.msg_box(f'Can\'t read profiles, the file "{FILE_NAME}" is corrupted. '
                             f'We will create a new empty properties file.', "L2FX",
                             l2helper.MB_ICONERROR)
            properties = Properties()
    else:
        print(f'ERROR: Can\'t find file "{FILE_NAME}". New one will be created.')
        properties = Properties()


def save_properties():
    global properties
    json_string = json.dumps(properties, default=vars)
    with open(FILE_NAME, 'w') as f:
        f.write(json_string)


def get_client(client: str) -> AccountRepository:
    if client not in properties.clients:
        c = AccountRepository([])
        properties.clients[client] = c
        return c
    return properties.clients[client]


def get_settings() -> Settings:
    return properties.settings


load_properties()

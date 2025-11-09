import builtins
import configparser
import sys

import l2helper
from datetime import datetime

import config
from config.types import AppType, LicenseType
from telemetry import ErrorReport

CONFIG_FILE = 'config.ini'


def str_to_bool(value: str) -> bool:
    if value:
        return value.lower() in ["true", "1", "yes", "y"]
    return False


def parse():
    config_parser = configparser.ConfigParser()
    config_parser.read(CONFIG_FILE)
    if config_parser.has_section("General"):
        if config_parser.has_option("General", "license_id"):
            config.LICENSE_ID = int(config_parser["General"]["license_id"])
            print(f'license_id: {config.LICENSE_ID}')
        if config_parser.has_option("General", "app_type"):
            app_type = config_parser["General"]["app_type"]
            if app_type in AppType.__members__:
                config.APP_TYPE = AppType[app_type]

            # Apply app name depends on app type
            if config.APP_TYPE == AppType.L2FX:
                config.APP_NAME = 'L2FX'
            elif config.APP_TYPE == AppType.TEZ:
                config.APP_NAME = 'L2eBot'

        if config_parser.has_option("General", "expires_at"):
            dt = config_parser["General"]["expires_at"].split('.')[0]  # get only date time and ignore micros
            config.EXPIRES_AT = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
            delta = config.EXPIRES_AT - datetime.utcnow()
            print(f'License expires at: {config.EXPIRES_AT} - [{delta.days} days left]')
            if config.EXPIRES_AT < datetime.utcnow():
                ErrorReport.send('Suspicious activity', 'Suspicious activity', f'EXPIRES_AT: {config.EXPIRES_AT}\rUTC_NOW: {datetime.utcnow()}')
                l2helper.msg_box(
                    f'ERROR: Your license ID:{config.LICENSE_ID} has expired.\r\nYou cannot use bot anymore.\r\nPlease prolong your license.',
                    config.APP_NAME, l2helper.MB_ICONERROR)
                sys.exit(0)
            if delta.days == 0:
                l2helper.msg_box(
                    f'WARNING: Your license will be expired in {int(delta.seconds/60/60)} hours.\r\n'
                    f'Please prolong your license.',
                    config.APP_NAME, l2helper.MB_ICONWARNING)
            elif delta.days <= 3:
                l2helper.msg_box(
                    f'WARNING: Your license will be expired in {delta.days} days.\r\nPlease prolong your license.',
                    config.APP_NAME, l2helper.MB_ICONWARNING)
        if config_parser.has_option("General", "license_type"):
            license_type = config_parser["General"]["license_type"]
            config.LICENSE_TYPE = LicenseType.from_string(license_type)
            print(f'license_type: {license_type}')
        if config_parser.has_option("General", "max_clients"):
            config.MAX_CLIENTS = int(config_parser["General"]["max_clients"])
            print(f'max_clients: { config.MAX_CLIENTS}')

        if config_parser.has_option("Capabilities", "script_auto_farm_2"):
            script_auto_farm_2 = str_to_bool(config_parser["Capabilities"]["script_auto_farm_2"])
            config.CAPABILITIES.SCRIPT_AUTO_FARM_2 = script_auto_farm_2
            if script_auto_farm_2:
                print(f'Capabilities: script_auto_farm_2 = {script_auto_farm_2}')
        if config_parser.has_option("Capabilities", "use_tether_driver"):
            use_tether_driver = str_to_bool(config_parser["Capabilities"]["use_tether_driver"])
            config.CAPABILITIES.USE_TETHER_DRIVER = use_tether_driver
            if use_tether_driver:
                print(f'Capabilities: use_tether_driver = {use_tether_driver}')
        if config_parser.has_option("Capabilities", "window_capture_2"):
            window_capture_2 = str_to_bool(config_parser["Capabilities"]["window_capture_2"])
            config.CAPABILITIES.WINDOW_CAPTURE_2 = window_capture_2
            if window_capture_2:
                print(f'Capabilities: window_capture_2 = {window_capture_2}')
        if config_parser.has_option("Capabilities", "f_clicker"):
            f_clicker = str_to_bool(config_parser["Capabilities"]["f_clicker"])
            config.CAPABILITIES.F_CLICKER = f_clicker
            if f_clicker:
                print(f'Capabilities: f_clicker = {f_clicker}')
        if config_parser.has_option("Capabilities", "z_auto_farm"):
            z_auto_farm = str_to_bool(config_parser["Capabilities"]["z_auto_farm"])
            config.CAPABILITIES.Z_AUTO_FARM = z_auto_farm
            if z_auto_farm:
                print(f'Capabilities: z_auto_farm = {z_auto_farm}')
        if getattr(builtins, 'l2fx_private', False):
            config.CAPABILITIES.PRIVATE = True
            print(f'Capabilities: l2fx_private = true')
        elif config_parser.has_option("Capabilities", "private"):
            private = str_to_bool(config_parser["Capabilities"]["private"])
            config.CAPABILITIES.PRIVATE = private
            if private:
                print(f'Capabilities: private = {private}')
        if config_parser.has_option("Capabilities", "unlocker"):
            unlocker = str_to_bool(config_parser["Capabilities"]["unlocker"])
            config.CAPABILITIES.UNLOCKER = unlocker
            if unlocker:
                print(f'Capabilities: unlocker = {unlocker}')

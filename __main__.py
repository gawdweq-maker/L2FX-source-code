import hashlib
import os
import sys
import webbrowser

import l2helper
from config import config_parser
import config
from config.types import LicenseType
from telemetry import StatReport, ErrorReport

try:
    config.SERVER_URL = globals().get('SERVER_URL')
    if not config.SERVER_URL:
        config.SERVER_URL = os.environ.get('L2FX_SERVER_URL')

    config.LICENSE = globals().get('LICENSE')
    if not config.LICENSE:
        # Allow either pre-hashed license (L2FX_LICENSE) or raw key (L2FX_LICENSE_KEY)
        lic_hash = os.environ.get('L2FX_LICENSE')
        if lic_hash:
            config.LICENSE = lic_hash
        else:
            lic_key = os.environ.get('L2FX_LICENSE_KEY')
            if lic_key:
                config.LICENSE = hashlib.sha1(lic_key.encode('UTF-8')).hexdigest()
            else:
                config.LICENSE = None

    config.HWID = globals().get('HWID')
    if not config.HWID:
        config.HWID = os.environ.get('L2FX_HWID')

    config.CLIENT_VER = globals().get('CLIENT_VER')
    if not config.CLIENT_VER:
        config.CLIENT_VER = os.environ.get('L2FX_CLIENT_VER')

    config_parser.parse()

    # Maybe install Tether Driver
    if config.CAPABILITIES.USE_TETHER_DRIVER:
        if l2helper.is_vs_redist_64_installed() is False:
            response = l2helper.msg_box("Microsoft Visual Studio Redistributable x64 not found.\n"
                                        "Would you like to download it?\n"
                                        "https://aka.ms/vs/17/release/vs_redist.x64.exe",
                                        config.APP_NAME, l2helper.MB_ICONERROR | l2helper.MB_YESNO)
            if response == l2helper.IDYES:
                webbrowser.open("https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170#latest-microsoft-visual-c-redistributable-version")
                ErrorReport.send('vs_redist.x64', "Microsoft Visual Studio Redistributable x64 not found",
                                 "User downloaded with browser")
            else:
                ErrorReport.send('vs_redist.x64', "Microsoft Visual Studio Redistributable x64 not found",
                                 "User declined downloading vs_redist.x64")
            sys.exit(1)

        import kbdmou.TetherInstaller

    # Notify about Beta version, if so
    if config.LICENSE_TYPE == LicenseType.BetaTest:
        l2helper.msg_box(
                    f'You are using Beta Test version.',
                    config.APP_NAME, l2helper.MB_ICONINFORMATION)

    StatReport.send_windows_info()
    StatReport.send_l2fx_client_info()

    # Run clicker or farm bot
    if config.CAPABILITIES.F_CLICKER:
        import f_clicker.clicker
    elif config.CAPABILITIES.UNLOCKER:
        import unlocker.callDll
    else:
        import farm_bot.essence_bot
except SystemExit:
    pass


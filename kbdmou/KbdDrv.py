from kbdmou import kbdmou_lib

status = None


def is_installed() -> bool:
    global status
    if kbdmou_lib.IsKbdDrvInstalled():
        status = 'Keyboard: Installed'
        return True
    else:
        status = 'Keyboard: Not found'
        return False


def install() -> bool:
    global status
    if kbdmou_lib.InstallKbdDrv():
        status = 'Keyboard: Installed'
        return True
    else:
        status = 'Keyboard: Install Error'
        return False


def remove() -> bool:
    global status
    if kbdmou_lib.RemoveKbdDrv():
        status = 'Keyboard: Removed'
        return True
    else:
        status = 'Keyboard: Remove Error'
        return False

from kbdmou import kbdmou_lib

status = None


def is_installed() -> bool:
    global status
    if kbdmou_lib.IsMouDrvInstalled():
        status = 'Mouse: Installed'
        return True
    else:
        status = 'Mouse: Not found'
        return False


def install() -> bool:
    global status
    if kbdmou_lib.InstallMouDrv():
        status = 'Mouse: Installed'
        return True
    else:
        status = 'Mouse: Install Error'
        return False


def remove() -> bool:
    global status
    if kbdmou_lib.RemoveMouDrv():
        status = 'Mouse: Removed'
        return True
    else:
        status = 'Mouse: Remove Error'
        return False

import platform

import sys
import ctypes
import time
from typing import Tuple

import pyscreeze
from PIL import Image
from ctypes import wintypes
from ctypes import *

import config
import l2helper
from telemetry import ErrorReport


pyscreeze.USE_IMAGE_NOT_FOUND_EXCEPTION = False

MB_ABORTRETRYIGNORE = 2
MB_CANCELTRYCONTINUE = 6
MB_HELP = 0x4000
MB_OK = 0
MB_OKCANCEL = 1
MB_RETRYCANCEL = 5
MB_YESNO = 4
MB_YESNOCANCEL = 3

MB_ICONEXCLAMATION = MB_ICONWARNING = 0x30
MB_ICONINFORMATION = MB_ICONASTERISK = 0x40
MB_ICONQUESTION = 0x20
MB_ICONSTOP = MB_ICONERROR = MB_ICONHAND = 0x10

MB_DEFBUTTON1 = 0
MB_DEFBUTTON2 = 0x100
MB_DEFBUTTON3 = 0x200
MB_DEFBUTTON4 = 0x300

MB_APPLMODAL = 0
MB_SYSTEMMODAL = 0x1000
MB_TASKMODAL = 0x2000

MB_DEFAULT_DESKTOP_ONLY = 0x20000
MB_RIGHT = 0x80000
MB_RTLREADING = 0x100000

MB_SETFOREGROUND = 0x10000
MB_TOPMOST = 0x40000
MB_SERVICE_NOTIFICATION = 0x200000

IDABORT = 3
IDCANCEL = 2
IDCONTINUE = 11
IDIGNORE = 5
IDNO = 7
IDOK = 1
IDRETRY = 4
IDTRYAGAIN = 10
IDYES = 6

WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_LBUTTONDBLCLK = 0x0203
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_RBUTTONDBLCLK = 0x0206
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_MBUTTONDBLCLK = 0x0209

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
shcore = ctypes.windll.shcore if float(platform.release()) > 7 else None

kernel32.GetTickCount64.restype = ctypes.c_ulonglong


def load_shcore():
    kernel32.LoadLibrary('ScCore.dll')
    pass

def is_x64() -> bool:
    return sys.maxsize > 2**32


if is_x64():
    l2helper_lib = CDLL(f'l2helper\\l2helper64.dll')
    print(l2helper_lib)
else:
    l2helper.msg_box("We are sorry, Windows x86 is not longer supported", "L2FX", MB_ICONERROR)
    sys.exit(0)


def find_lineage2_windows() -> [wintypes.HWND]:
    if not l2helper_lib:
        return []

    class_names = [
        b'l2UnrealWWindowsViewportWindow',
        b'L2UnrealWWindowsViewportWindow',
        b'mwUnrealWWindowsViewportWindow',  # MasterWork
        b'UnrealWindow'
        # b'Notepad',
        # b'POEWindowClass'
    ]
    arr = []

    for class_name in class_names:
        size = c_int()
        l2helper_lib.findWindowsByClass(class_name, 0, ctypes.pointer(size))

        hwnd_list = (wintypes.HWND * size.value)()
        l2helper_lib.findWindowsByClass(class_name, ctypes.pointer(hwnd_list), ctypes.pointer(size))

        for hwnd in hwnd_list:
            arr.append(hwnd)

    return arr


def activate_window(hwnd: wintypes.HWND):
    l2helper_lib.activateWindow(0)
    time.sleep(.1)
    l2helper_lib.activateWindow(hwnd)


def activate_window3(hwnd: wintypes.HWND):
    l2helper_lib.activateWindow3(hwnd)


def is_window_active(hwnd: wintypes.HWND) -> bool:
    return hwnd == user32.GetForegroundWindow()


def get_show_cmd(hwnd: wintypes.HWND) -> int:
    return l2helper_lib.getShowCmd(hwnd)


def set_show_cmd(hwnd: wintypes.HWND, show_cmd: int) -> bool:
    return l2helper_lib.setShowCmd(hwnd, show_cmd)


def create_window_observer(hwnd: wintypes.HWND, refresh_interval_ms=250) -> wintypes.HANDLE:
    if config.CAPABILITIES.WINDOW_CAPTURE_2:
        return start_observer(hwnd)

    return l2helper_lib.createWindowObserver(hwnd, refresh_interval_ms)


def release_window_observer(hwnd: wintypes.HWND) -> bool:
    if config.CAPABILITIES.WINDOW_CAPTURE_2:
        return stop_observer(hwnd)

    return l2helper_lib.releaseWindowObserver(hwnd)


def capture_window_observer(hwnd: wintypes.HWND) -> Image:
    if config.CAPABILITIES.WINDOW_CAPTURE_2:
        return capture(hwnd)

    # st = time.time()
    size = c_int()
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.pointer(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    l2helper_lib.captureWindowObserver(hwnd, 0, ctypes.pointer(size))

    if size.value <= 0:
        return None

    # if window been resized, but still used old buffer
    required_buf_size = width * height * 3
    if size.value < required_buf_size:
        return None

    buf = (ctypes.c_ubyte * size.value)()
    if l2helper_lib.captureWindowObserver(hwnd, ctypes.pointer(buf), ctypes.pointer(size)) == 0:
        print(f'Unable to capture window(hwnd:{hwnd})')
        return None

    bitmap = bytes(buf)

    if width == 0 or height == 0:
        return None

    #print(f'bitmap: {len(bitmap)}, size: {width}x{height}')
    try:
        img = Image.frombytes('RGB', (width, height), bitmap, 'raw')
    except ValueError as e:
        print(f'bitmap: {len(bitmap)}, size: {width}x{height}')
        print(e)
        img = None

    # print(f'capture_window observer: {time.time() - st}')
    return img


def set_window_observer_interval(hwnd: wintypes.HWND, refresh_interval_ms: int) -> bool:
    return l2helper_lib.setWindowObserverInterval(hwnd, refresh_interval_ms)


def capture_window(hwnd: wintypes.HWND) -> Image:
    st = time.time()
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.pointer(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top

    size = c_int()
    if l2helper_lib.captureWindow(hwnd, 0, ctypes.pointer(size)) == 0:
        print(f'Unable to capture window(hwnd:{hwnd}) try to extend buffer')

    if size.value <= 0:
        return None

    buf = (ctypes.c_ubyte * size.value)()
    if l2helper_lib.captureWindow(hwnd, ctypes.pointer(buf), ctypes.pointer(size)) == 0:
        print(f'Unable to capture window(hwnd:{hwnd})')
        return None

    bitmap = bytes(buf)
    img = Image.frombytes('RGB', (width, height), bitmap, 'raw')
    print(f'capture_window: {time.time()-st}')
    return img


def get_window_title(hwnd: wintypes.HWND):
    buf = (ctypes.c_wchar * 255)()
    user32.GetWindowTextW(hwnd, ctypes.pointer(buf), 255)
    return buf.value


def locate_center(l2_img: Image, img_to_find: Image, confidence=1.0) -> Tuple[int, int] or None:
    box = pyscreeze.locate(img_to_find, l2_img, confidence=confidence, grayscale=False)
    if box is None:
        return None

    x = int(box.left + box.width / 2)
    y = int(box.top + box.height / 2)
    return x, y


def locate(l2_img: Image, img_to_find: Image, confidence=1) -> Tuple[int, int, int, int] or None:
    box = pyscreeze.locate(img_to_find, l2_img, confidence=confidence)
    if box is None:
        return None

    return box


def client_to_screen(hwnd: wintypes.HWND) -> Tuple[int, int]:
    point = wintypes.POINT()
    user32.ClientToScreen(hwnd, ctypes.pointer(point))
    return point.x, point.y


def client_center(hwnd: wintypes.HWND) -> Tuple[int, int]:
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.pointer(rect))
    x = (rect.right - rect.left)/2 + rect.left
    y = (rect.bottom - rect.top)/2 + rect.top
    return x, y


def client_size(hwnd: wintypes.HWND) -> Tuple[int, int]:
    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.pointer(rect))
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    return width, height


def switch_keyboard_to_english(hwnd: wintypes.HWND) -> bool:
    return l2helper_lib.switchKeyboardToEnglish(hwnd)


def is_caps_lock_on() -> bool:
    return l2helper_lib.isCapsLockOn()


def msg_box(text, title, style):
    return user32.MessageBoxW(None, text, title, style)


# @ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_int)
# def callback(a, b):
#     print("foo has finished its job (%d, %d)" % (a, b))


def register_kbd_hotkey(callback, modifier=0x0001 | 0x4000, vk=0x30):
    # modifier = 0x0001 | 0x4000   # MOD_ALT | MOD_NOREPEAT
    # vk = 0x30                    # 0
    l2helper_lib.registerKbdHotKey(callback, modifier, vk)


def unregister_kbd_hotkey():
    l2helper_lib.unregisterKbdHotKey()


def register_mou_hook(callback, wm_event):
    l2helper_lib.registerMouseHook(callback, wm_event)


def unregister_mou_hook(wm_event):
    l2helper_lib.unregisterMouseHook(wm_event)


def get_windows_screen_scaling() -> float:
    if shcore:
        return shcore.GetScaleFactorForDevice(0) / 100
    else:
        return 1.0


def hwnd_to_path(hwnd: ctypes.wintypes.HWND, origin=None) -> str or None:
    pid = c_long()
    if user32.GetWindowThreadProcessId(hwnd, ctypes.pointer(pid)) == 0:
        error = kernel32.GetLastError()
        ErrorReport.send("Binary path error", "user32.GetWindowThreadProcessId", f"user32.GetWindowThreadProcessId({hwnd}) -> error: {error}, origin: {origin}")
        return None

    get_process_image_path = l2helper_lib.GetProcessImagePath
    get_process_image_path.restype = c_int
    get_process_image_path.argtypes = [c_long, c_void_p, c_longlong]

    path_buffer = (ctypes.c_wchar * 512)()
    ret = get_process_image_path(pid.value, ctypes.pointer(path_buffer), 512)
    if ret != 0:
        error = kernel32.GetLastError()
        ErrorReport.send("Binary path error", "GetProcessImagePath", f"GetProcessImagePath({pid}) -> {ret}, error: {error}, origin: {origin}")
        return None

    path = path_buffer.value
    return path

def start_observer(hwnd: wintypes.HWND) -> wintypes.HANDLE:
    return l2helper_lib.StartObserver(hwnd)


def stop_observer(hwnd: wintypes.HWND) -> bool:
    return l2helper_lib.StopObserver(hwnd)


def capture(hwnd: wintypes.HWND) -> Image:
    size = c_int()
    img_width = c_int()
    img_height = c_int()

    rect = wintypes.RECT()
    user32.GetClientRect(hwnd, ctypes.pointer(rect))
    window_width = rect.right - rect.left
    window_height = rect.bottom - rect.top

    guess_size = window_width * window_height * 3
    if guess_size <= 0:
        return None

    buf = (ctypes.c_ubyte * guess_size)()
    size.value = guess_size

    if not l2helper_lib.Capture(hwnd, ctypes.pointer(buf), ctypes.pointer(size), ctypes.pointer(img_width), ctypes.pointer(img_height)):
        if size.value > guess_size:
            # Looks like window was resized, try re-alloc buffer and capture one more time
            buf = (ctypes.c_ubyte * size.value)()
            if not l2helper_lib.Capture(hwnd, ctypes.pointer(buf), ctypes.pointer(size), ctypes.pointer(img_width),
                                        ctypes.pointer(img_height)):
                print(f'Unable to capture window(hwnd:{hwnd})')
                return None

    if size.value <= 0:
        return None

    bitmap = bytes(buf)

    if img_width.value == 0 or img_height.value == 0:
        return None

    try:
        img = Image.frombytes('RGB', (img_width.value, img_height.value), bitmap, 'raw')
    except ValueError as e:
        print(f'bitmap: {len(bitmap)}, size: {img_width.value}x{img_height.value}')
        print(e)
        img = None

    # print(f'capture_window observer: {time.time() - st}')
    return img


def is_tp_in_progress(hwnd: wintypes.HWND) -> bool:
    return l2helper_lib.isTpInProgress(hwnd)


def is_to_done(hwnd: wintypes.HWND) -> bool:
    return l2helper_lib.isTpDone(hwnd)


def is_vs_redist_64_installed() -> bool:
    return bool(l2helper_lib.isVsRedist64Installed())


def get_desktop_hwnd() -> wintypes.HWND:
    hwnd = user32.FindWindowW("Progman", None)
    if not hwnd:
        user32.FindWindoExW(0, 0, "WorkerW", None)
    return hwnd


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', ctypes.c_uint), ('dwTime', ctypes.c_uint)]


def get_idle_duration() -> int:
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not user32.GetLastInputInfo(ctypes.byref(lii)):
        return 0
    millis = kernel32.GetTickCount64() - lii.dwTime
    return millis / 1000.0

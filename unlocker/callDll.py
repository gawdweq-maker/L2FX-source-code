import time

import sys

import sys
import ctypes
import os
# import keyboard  # Установите библиотеку: pip install keyboard
from ctypes import wintypes

import l2helper

MB_ICONSTOP = MB_ICONERROR = MB_ICONHAND = 0x10

# Загружаем DLL
# script_dir = os.path.dirname(os.path.realpath(__file__))
# dll_path = os.path.join(script_dir, "UL.dll")
# hook_dll = ctypes.WinDLL(dll_path)

def is_x64() -> bool:
    return sys.maxsize > 2**32


if is_x64():
    unlocker_lib = ctypes.CDLL(f'unlocker\\UL.dll')
    print(unlocker_lib)
else:
    l2helper.msg_box("We are sorry, Windows x86 is not longer supported", "L2FX", MB_ICONERROR)
    sys.exit(0)

# Флаг для контроля работы
is_running = False


def stop_hooks():
    global is_running
    if is_running:
        print("Останавливаем хуки...")
        unlocker_lib.StopKeyboardAndMouse()
        is_running = False


def start_hooks():
    global is_running
    if not is_running:
        print("Запускаем хуки...")
        result = unlocker_lib.StartKeyboardAndMouse()
        if result == 0:
            is_running = True
        else:
            print(f"Ошибка инициализации: код {result}")

# Регистрируем хоткей Ctrl+Shift+Q для остановки
# keyboard.add_hotkey('ctrl+shift+q', stop_hooks)

print("Управление:")
print("1. Хуки запустятся автоматически при вызове start_hooks()")
print("2. Нажмите Ctrl+Shift+Q для остановки")
# Пример использования

try:
    start_hooks()  # Запускаем при старте
    while True:
        time.sleep(.1)
        pass
except KeyboardInterrupt:
    pass
finally:
    print('Closing unlocker')
    stop_hooks()  # На всякий случай останавливаем при Ctrl+C


# Бесконечный цикл, чтобы программа не завершалась
# try:
#     while True:
#         keyboard.wait()  # Ожидаем событий клавиатуры
#         pass
# except KeyboardInterrupt:
#     stop_hooks()  # На всякий случай останавливаем при Ctrl+C
#     pass

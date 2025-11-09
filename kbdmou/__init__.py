from ctypes import *
import sys

import config
import l2helper


def is_x64() -> bool:
	return sys.maxsize > 2**32


if is_x64():
	if config.CAPABILITIES.USE_TETHER_DRIVER:
		kbdmou_lib = CDLL(f'kbdmou\\kbdmou64_tether.dll')
	else:
		kbdmou_lib = CDLL(f'kbdmou\\kbdmou64.dll')
	print(kbdmou_lib)
else:
	l2helper.msg_box("We are sorry, Windows x86 is not longer supported", "L2FX", l2helper.MB_ICONERROR)
	sys.exit(0)


def connect_kbd_mou() -> bool:
	return kbdmou_lib.ConnectMouKbd()

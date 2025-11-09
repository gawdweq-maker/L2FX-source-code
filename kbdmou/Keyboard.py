import time
from . import kbdmou_lib, KbdDrv as Driver
Driver.__repr__

KEY_NAMES = [
    "F1",
	"F2",
	"F3",
	"F4",
	"F5",
	"F6",
	"F7",
	"F8",
	"F9",
	"F10",
	"F11",
	"F12",
	"LEFT",
	"RIGHT",
	"UP",
	"DOWN",
	"SHIFT",
	"CTRL",
	"ALT",
	"PGUP",
	"PGDN",
	"HOME",
	"END",
	"INSERT",
	"DEL",
	"BACKSPACE",
	"TAB",
	"ENTER",
	"ESC",
	"SPACE",
	" ",
	"'",
	",",
	"-",
	".",
	"/",
	"0",
	"1",
	"2",
	"3",
	"4",
	"5",
	"6",
	"7",
	"8",
	"9",
	";",
	"=",
	"[",
	"\\"
	"]",
	"`",
	"A",
	"B",
	"C",
	"D",
	"E",
	"F",
	"G",
	"H",
	"I",
	"J",
	"K",
	"L",
	"M",
	"N",
	"O",
	"P",
	"Q",
	"R",
	"S",
	"T",
	"U",
	"V",
	"W",
	"X",
	"Y",
	"Z",
	"CAPS"
]


def input(*args):
	kbdmou_lib.KbdInput(*args, 0)


def keyDown(key):
	"""Performs a keyboard key press without the release. This will put that
	key in a held down state.

	NOTE: For some reason, this does not seem to cause key repeats like would
	happen if a keyboard key was held down on a text field.

	Args:
		key (str): The key to be pressed down. The valid names are listed in
		KEYBOARD_KEYS.

	Returns:
		None
	"""
	if len(key) > 1:
		key = key.lower()

	kbdmou_lib.KbdKeyDown(key)


def keyUp(key, logScreenshot=None, _pause=True):
	"""Performs a keyboard key release (without the press down beforehand).

	Args:
		key (str): The key to be released up. The valid names are listed in
		KEYBOARD_KEYS.

	Returns:
		None
	"""
	if len(key) > 1:
		key = key.lower()

	kbdmou_lib.KbdKeyUp(key)


def press(keys, presses=1, interval=0.0):
	"""Performs a keyboard key press down, followed by a release.

	Args:
		key (str, list): The key to be pressed. The valid names are listed in
		KEYBOARD_KEYS. Can also be a list of such strings.
		presses (integer, optional): The number of press repetitions.
		1 by default, for just one press.
		interval (float, optional): How many seconds between each press.
		0.0 by default, for no pause between presses.
		pause (float, optional): How many seconds in the end of function process.
		None by default, for no pause in the end of function process.
	Returns:
		None
	"""
	if type(keys) == str:
		if len(keys) > 1:
			keys = keys.lower()
		keys = [keys] # If keys is 'enter', convert it to ['enter'].
	else:
		lower_keys = []
		for s in keys:
			if len(s) > 1:
				lower_keys.append(s.lower())
			else:
				lower_keys.append(s)
		keys = lower_keys
	interval = float(interval)
	for i in range(presses):
		for k in keys:
			keyDown(k)
			keyUp(k)
		time.sleep(interval)
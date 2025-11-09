import ctypes
import time
import numpy as np
from . import kbdmou_lib, MouDrv as Driver
from ctypes import windll, Structure, c_long, byref
Driver.__repr__

MOUSE_MOVE_RELATIVE = 0
MOUSE_MOVE_ABSOLUTE = 1

MOUSE_LEFT_BUTTON_DOWN = 0x0001
MOUSE_LEFT_BUTTON_UP = 0x0002
MOUSE_RIGHT_BUTTON_DOWN = 0x0004
MOUSE_RIGHT_BUTTON_UP = 0x0008
MOUSE_MIDDLE_BUTTON_DOWN = 0x0010
MOUSE_MIDDLE_BUTTON_UP = 0x0020

LEFT = 0
RIGHT = 1
MIDDLE = 2

SM_CXSCREEN = 0
SM_CYSCREEN = 1


class POINT(Structure):
    _fields_ = [("x", c_long), ("y", c_long)]


def normalize_xy(x, y):
    x = int(x * 0xffff / ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN))
    y = int(y * 0xffff / ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN))
    return x, y


def position(x=None, y=None):
    """
        Returns the current xy coordinates of the mouse cursor as a two-integer tuple.

        Args:
          x (int, None, optional) - If not None, this argument overrides the x in
            the return value.
          y (int, None, optional) - If not None, this argument overrides the y in
            the return value.

        Returns:
          (x, y) tuple of the current xy coordinates of the mouse cursor.

        NOTE: The position() function doesn't check for failsafe.
        """
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    pt.x = int(pt.x)
    pt.y = int(pt.y)
    if x is not None:  # If set, the x parameter overrides the return value.
        pt.x = int(x)
    if y is not None:  # If set, the y parameter overrides the return value.
        pt.y = int(y)
    return pt.x, pt.y


def human_click_duration(mean=85, q1=75, q3=95):
    """
    Simulates a mouse click duration based on a Gaussian distribution.
    Source:
    Link:   https://ieeexplore.ieee.org/document/9851764

    :param mean:    Mean duration of the click (default 85 ms)
    :param q1:      First quartile of the click duration (default 75 ms)
    :param q3:      Third quartile of the click duration (default 95 ms)
    :return:        A simulated mouse click duration
    """
    # Standard deviation approximation
    std_dev = (q3 - q1) / 2

    # Simulating one click duration
    click_duration = np.random.normal(mean, std_dev)

    # Ensuring the click duration is within realistic bounds
    click_duration = max(55, min(click_duration, 135))

    return click_duration/1000


def mouse_down(x=None, y=None, button=LEFT):
    """Performs pressing a mouse button down (but not up).

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        mouse down happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        mouse down happens. None by default.
      button (str, int, optional): The mouse button pressed down.

    Returns:
      None

    Raises:
      PyAutoGUIException: If button is not one of 'left', 'middle', 'right', 1, 2, or 3
    """

    if button is LEFT:
        button = MOUSE_LEFT_BUTTON_DOWN
    elif button is RIGHT:
        button = MOUSE_RIGHT_BUTTON_DOWN
    elif button is MIDDLE:
        button = MOUSE_MIDDLE_BUTTON_DOWN

    if x is None or y is None:
        kbdmou_lib.MouInput(button, 0, 0, 0)
    else:
        x, y = normalize_xy(x, y)
        kbdmou_lib.MouInput(button, MOUSE_MOVE_ABSOLUTE, x, y)


def mouse_up(x=None, y=None, button=LEFT):
    """Performs releasing a mouse button up (but not down beforehand).

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        mouse up happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        mouse up happens. None by default.
      button (str, int, optional): The mouse button released.

    Returns:
      None

    Raises:
      PyAutoGUIException: If button is not one of 'left', 'middle', 'right', 1, 2, or 3
    """

    if button is LEFT:
        button = MOUSE_LEFT_BUTTON_UP
    elif button is RIGHT:
        button = MOUSE_RIGHT_BUTTON_UP
    elif button is MIDDLE:
        button = MOUSE_MIDDLE_BUTTON_UP

    if x is None or y is None:
        kbdmou_lib.MouInput(button, 0, 0, 0)
    else:
        x, y = normalize_xy(x, y)
        kbdmou_lib.MouInput(button, MOUSE_MOVE_ABSOLUTE, x, y)


def click(x=None, y=None, clicks=1, interval=human_click_duration(), button=LEFT, click_duration=human_click_duration()):
    """
     Performs pressing a mouse button down and then immediately releasing it. Returns ``None``.

     When no arguments are passed, the primary mouse button is clicked at the mouse cursor's current location.

     If integers for ``x`` and ``y`` are passed, the click will happen at that XY coordinate. If ``x`` is a string, the
     string is an image filename that PyAutoGUI will attempt to locate on the screen and click the center of. If ``x``
     is a sequence of two coordinates, those coordinates will be used for the XY coordinate to click on.

     The ``clicks`` argument is an int of how many clicks to make, and defaults to ``1``.

     The ``interval`` argument is an int or float of how many seconds to wait in between each click, if ``clicks`` is
     greater than ``1``. It defaults to ``0.0`` for no pause in between clicks.

     The ``button`` argument is one of the constants ``LEFT``, ``MIDDLE``, ``RIGHT``, ``PRIMARY``, or ``SECONDARY``.
     It defaults to ``PRIMARY`` (which is the left mouse button, unless the operating system has been set for
     left-handed users.)

     If ``x`` and ``y`` are specified, and the click is not happening at the mouse cursor's current location, then
     the ``duration`` argument is an int or float of how many seconds it should take to move the mouse to the XY
     coordinates. It defaults to ``0`` for an instant move.

     If ``x`` and ``y`` are specified and ``duration`` is not ``0``, the ``tween`` argument is a tweening function
     that specifies the movement pattern of the mouse cursor as it moves to the XY coordinates. The default is a
     simple linear tween. See the PyTweening module documentation for more details.

     The ``pause`` parameter is deprecated. Call the ``time.sleep()``.

     Raises:
       PyAutoGUIException: If button is not one of 'left', 'middle', 'right', 1, 2, 3
     """
    if x and y:
        move_to(x, y)
        time.sleep(interval)
    for i in range(clicks):
        if button in (LEFT, MIDDLE, RIGHT):
            mouse_down(x, y, button)
            time.sleep(click_duration)
            mouse_up(x, y, button)

        time.sleep(interval)


def left_click(x=None, y=None, click_duration=human_click_duration()):
    """Performs a left mouse button click.

    This is a wrapper function for click('left', x, y).

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.
      click_duration (float, optional): The amount of time between mouse down
        and mouse up. 0.0 by default.

    Returns:
      None
    """
    click(x, y, 1, 0.0, LEFT, click_duration)


def right_click(x=None, y=None, click_duration=human_click_duration()):
    """Performs a right mouse button click.

    This is a wrapper function for click('right', x, y).

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.
      click_duration (float, optional): The amount of time between mouse down
        and mouse up. 0.0 by default.

    Returns:
      None
    """
    click(x, y, 1, 0.0, RIGHT, click_duration)


def middle_click(x=None, y=None, click_duration=human_click_duration()):
    """Performs a middle mouse button click.

    This is a wrapper function for click('middle', x, y).

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.
      click_duration (float, optional): The amount of time between mouse down
        and mouse up. 0.0 by default.

    Returns:
      None
    """
    click(x, y, 1, 0.0, MIDDLE, click_duration)


def double_click(x=None, y=None, interval=human_click_duration(), button=LEFT, click_duration=human_click_duration()):
    """Performs a double click.

    This is a wrapper function for click('left', x, y, 2, interval).

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.
      interval (float, optional): The number of seconds in between each click,
        if the number of clicks is greater than 1. 0.0 by default, for no
        pause in between clicks.
      click_duration (float, optional): The amount of time between mouse down
        and mouse up. 0.0 by default.
      button (str, int, optional): The mouse button released.

    Returns:
      None

    Raises:
      PyAutoGUIException: If button is not one of 'left', 'middle', 'right', 1, 2, 3, 4,
        5, 6, or 7
    """
    click(x, y, 2, interval, button, click_duration)


def move_to(x, y):
    """Moves the mouse cursor to a point on the screen.

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x (int, float, None, tuple, optional): The x position on the screen where the
        click happens. None by default. If tuple, this is used for x and y.
        If x is a str, it's considered a filename of an image to find on
        the screen with locateOnScreen() and click the center of.
      y (int, float, None, optional): The y position on the screen where the
        click happens. None by default.

    Returns:
      None
    """
    x, y = normalize_xy(x, y)
    kbdmou_lib.MouInput(0, MOUSE_MOVE_ABSOLUTE, x, y)


def move_rel(x_offset=None, y_offset=None):
    """Moves the mouse cursor to a point on the screen, relative to its current
    position.

    The x and y parameters detail where the mouse event happens. If None, the
    current mouse position is used. If a float value, it is rounded down. If
    outside the boundaries of the screen, the event happens at edge of the
    screen.

    Args:
      x_offset (int, float, None, tuple, optional): How far left (for negative values) or
        right (for positive values) to move the cursor. 0 by default. If tuple, this is used for x and y.
      y_offset (int, float, None, optional): How far up (for negative values) or
        down (for positive values) to move the cursor. 0 by default.

    Returns:
      None
    """
    kbdmou_lib.MouInput(0, MOUSE_MOVE_RELATIVE, x_offset, y_offset)

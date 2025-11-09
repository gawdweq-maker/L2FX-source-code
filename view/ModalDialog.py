from tkinter import Toplevel, Tk
from typing import overload


class ModalDialog(Toplevel):

    def __init__(self, parent: Tk):
        super().__init__(parent)
        self.parent = parent

        parent.wm_attributes('-disabled', 1)
        self.transient(parent)
        self.protocol('WM_DELETE_WINDOW', self.close_dialog)

        self.grab_set()
        self.focus_force()

    @overload
    def wm_geometry(self, new_geometry=None) -> str: ...

    def wm_geometry(self, new_geometry=None) -> str:
        if isinstance(new_geometry, str):
            values = new_geometry.split('+')
            if len(values) == 1:
                width, height = values[0].split('x')

                # set in the center of parent window
                x = self.parent.winfo_x() + int((self.parent.winfo_width() - int(width)) / 2)
                y = self.parent.winfo_y() + int((self.parent.winfo_height() - int(height)) / 2)
                return super().wm_geometry(f'{width}x{height}+{x}+{y}')

        return super().wm_geometry(new_geometry)

    geometry = wm_geometry

    def close_dialog(self):
        self.grab_release()
        self.parent.wm_attributes('-disabled', 0)
        self.destroy()
        self.parent.deiconify()
        self.parent.focus_force()
        pass

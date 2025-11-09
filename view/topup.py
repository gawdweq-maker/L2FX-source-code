from datetime import datetime

import http.client

import config
from tkinter import Tk, Frame, Label, Entry, Button, messagebox
from tkinter.constants import NW, LEFT, END
from view.ModalDialog import ModalDialog

from view.ui import Icons


class CodeEntry(Entry):
    def __init__(self, master=None, placeholder="XXXX-XXXX-XXXX-XXXX-XXXX", color="grey", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']
        self.has_placeholder = False

        self.bind("<FocusIn>", self._focus_in)
        self.bind("<FocusOut>", self._focus_out)
        self.bind("<KeyRelease>", self._key_release)

        self._show_placeholder()

    def _show_placeholder(self):
        if not self.get() and not self.focus_get() == self:
            self.has_placeholder = True
            self.config(fg=self.placeholder_color)
            self.delete(0, END)
            self.insert(0, self.placeholder)
            self.icursor(0)
        else:
            self.has_placeholder = False

    def _hide_placeholder(self):
        if self.has_placeholder:
            self.delete(0, END)
            self.config(fg=self.default_fg_color)
            self.has_placeholder = False

    def _focus_in(self, event=None):
        self._hide_placeholder()

    def _focus_out(self, event=None):
        self._show_placeholder()

    def _key_release(self, event=None):
        if not self.get() and not self.focus_get() == self:
            self._show_placeholder()
        elif not self.get() and self.has_placeholder:
            self._hide_placeholder()

    def get_value(self):
        if self.has_placeholder:
            return ""
        return self.get()


class TopUpDialog(ModalDialog):

    def __init__(self, parent: Tk):
        super().__init__(parent)

        # self.geometry(f'250x260')
        self.title("Settings")
        self.wm_attributes('-toolwindow', 1)
        self.resizable(width=False, height=False)

        width = 230
        height = 115
        self.resizable(False, False)
        self.withdraw()
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.deiconify()

        msg_frame = Frame(self)
        msg_frame.pack(padx=20, pady=(10, 5), anchor=NW)

        Label(msg_frame, image=Icons.topup, compound=LEFT).grid(row=0, column=0)
        Label(msg_frame, text=f'Please enter activation code', anchor='w', justify='left').grid(row=0, column=1, padx=5)

        frame_code = Frame(self)
        frame_code.pack(padx=20, pady=(0, 10), anchor=NW)
        # Label(frame_code, text="Code", width=5, anchor='w').pack(side=LEFT)
        entry_code = CodeEntry(frame_code, width=30)
        entry_code.pack(side=LEFT, padx=3)
        # entry_code.focus()

        frame_btn = Frame(self)
        frame_btn.pack(pady=(7, 7))
        btn_send = Button(frame_btn,
                          text='Activate', width=10,
                          command=lambda: self.code_on_send(
                              config.LICENSE,
                              entry_code.get_value().strip(" "))
                          )
        btn_send.pack(side=LEFT, padx=(0, 10))
        btn_exit = Button(frame_btn, text='Cancel', width=10, command=self.close_dialog)
        btn_exit.pack(side=LEFT)

        self.bind("<Return>", lambda event: self.code_on_send(
            config.LICENSE,
            entry_code.get_value().strip(" "))
        )

    def code_on_send(self, hash_id, code):
        # Validate code
        if not code.strip(" "):
            messagebox.showerror("Validation Error", "Code must not be empty.")
            return

        parts = code.split('-')
        if len(parts) != 5:
            messagebox.showerror("Validation Error", "Code must be in the format XXXX-XXXX-XXXX-XXXX-XXXX.")
            return

        valid_chars = "ABCDEFGHJKLMNOPQRSTUVWXYZ234567890"
        for part in parts:
            if len(part) != 4 or not all(c in valid_chars for c in part):
                messagebox.showerror("Validation Error", "Code must contains only allowed characters.")
                return

        try:
            url = f'{config.SERVER_URL}/redeem/{code}'

            # Split the URL into host and path
            if url.startswith('http://'):
                url = url[7:]
                secure = False
            elif url.startswith('https://'):
                url = url[8:]
                secure = True
            else:
                raise ValueError('Url must start with http:// or https://')

            host, _, path = url.partition('/')
            path = '/' + path

            if secure:
                conn = http.client.HTTPSConnection(host)
            else:
                conn = http.client.HTTPConnection(host)

            headers = {'hash-id': hash_id}
            conn.request("POST", path, headers=headers)
            resp = conn.getresponse()

            content_type = resp.getheader('Content-Type')
            status_code = resp.status
            resp_data = resp.read().decode('utf-8')

            if status_code == 200:
                if 'expires-at' in resp.headers:
                    expires_at = resp.headers['expires-at']
                    config.EXPIRES_AT = datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S')

                messagebox.showinfo('Success', resp_data)
                self.close_dialog()
            else:
                messagebox.showerror('L2FE Error', resp_data)
            conn.close()

        except Exception as err:
            raise SystemExit(err)
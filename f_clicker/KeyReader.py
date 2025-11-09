from tkinter import Entry, StringVar, END


def keycode_to_keysym(keycode):
    special_keys = {
        8:   'Backspace',
        9:   'Tab',
        12:  '5',  # Num 5
        13:  'Enter',
        16:  'Shift',
        17:  'Ctrl',
        18:  'Alt',
        19:  'Pause',
        20:  'CapsLock',
        27:  'Esc',
        32:  'Space',
        33:  'PageUp',
        34:  'PageDown',
        35:  'End',
        36:  'Home',
        37:  'Left',
        38:  'Up',
        39:  'Right',
        40:  'Down',
        45:  'Insert',
        46:  'Delete',
        91:  'Windows',
        92:  'RightWindows',
        93:  'Menu',
        96:  'Num0',
        97:  'Num1',
        98:  'Num2',
        99:  'Num3',
        100: 'Num4',
        101: 'Num5',
        102: 'Num6',
        103: 'Num7',
        104: 'Num8',
        105: 'Num9',
        106: 'Num*',
        107: 'Num+',
        109: 'Num-',
        110: 'Num.',
        111: 'Num/',
        144: 'NumLock',
        186: ';',
        187: '=',
        188: '<',
        189: '-',
        190: '>',
        191: '/',
        192: '`',
        219: '[',
        220: '\\',
        221: ']',
        222: '\'',
    }

    if keycode in special_keys:
        return special_keys[keycode]

    if 48 <= keycode <= 57:
        return chr(keycode)

    if 65 <= keycode <= 90:
        return chr(keycode)

    if 112 <= keycode <= 123:
        return 'F' + str(keycode - 111)

    return f'Unknown ({keycode})'


class KeyReader(Entry):
    def __init__(self, master=None, root=None, callback=None, **kw):
        self.entry_var = StringVar()
        self.placeholder_text = '<Set Key>'
        self.ctrl = False
        self.shift = False
        self.alt = False
        self.key = 0
        self.root = root
        self.on_change_callback = callback
        super().__init__(master, **kw, textvariable=self.entry_var, width=12)
        self.bind('<FocusIn>', self.on_focusin)
        self.bind('<FocusOut>', self.on_focusout)

        self.on_focusout(None)

    def on_key_press(self, event):
        key_pressed = ""
        self.ctrl = False
        self.shift = False
        self.alt = False

        if event.state & 0x0004 or event.keycode == 17:
            key_pressed += "Ctrl+"
            self.ctrl = True
        if event.state & 0x0001 or event.keycode == 16:
            key_pressed += "Shift+"
            self.shift = True
        if event.state & 0x00020000 or event.keycode == 18:
            key_pressed += "Alt+"
            self.alt = True

        # Ignore pure Shift/Ctrl/Alt BackSpace, Delete`
        if event.keycode not in (16, 17, 18, 8, 46):
            key_pressed += keycode_to_keysym(event.keycode)
            self.key = event.keycode
        else:
            self.key = 0

        self.entry_var.set(key_pressed)
        self.icursor(len(key_pressed))

        # Prevent opening menu on Alt press
        if event.keysym == 'Alt_L' or event.keysym == 'Alt_R':
            return "break"
        self.on_change_callback()

    def on_key_release(self, event):
        if self.key == 0:
            self.entry_var.set("")

    def on_focusin(self, event):
        # self.entry_var.set("")
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.bind('<KeyRelease>', self.on_key_release)

        if self.get() == self.placeholder_text:
            self.delete(0, END)
            self.config(fg='black')

    def on_focusout(self, event):
        self.root.unbind('<KeyPress>')
        self.root.unbind('<KeyRelease>')

        if not self.get():
            self.insert(0, self.placeholder_text)
            self.config(fg='grey')

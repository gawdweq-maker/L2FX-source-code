from tkinter import TOP, Button, Tk, Label, Frame, StringVar, Entry, W, Text, NW, E, END, font
from PIL import ImageTk, Image
import config
import l2helper
from scripts import L2Window, utils
from telemetry import ErrorReport
from view.ModalDialog import ModalDialog
from view.ui import Icons


class ReportDialog(ModalDialog):
    __title_var: StringVar
    __message_var: StringVar
    __textbox: Text

    __screenshot: Image
    __title: str
    __message: str

    def __init__(self, parent: Tk, screenshot: Image):
        super().__init__(parent)

        self.__screenshot = screenshot

        dialog_width = 350
        k = screenshot.width / screenshot.height
        img_width = dialog_width
        img_height = int(img_width / k)

        # self.geometry(f'{img_width}x{img_height+210}')
        self.title("Send bug report")
        self.wm_attributes('-toolwindow', 1)
        self.resizable(width=False, height=False)

        self.__title_var = StringVar(value='')
        self.__message_var = StringVar(value='')
        default_font = font.nametofont("TkDefaultFont")

        label = Label(self, text='Screenshot here', borderwidth=2, relief="solid", height=13)
        resized_image = screenshot.resize((img_width, img_height))
        if resized_image is not None:
            thumbnail = ImageTk.PhotoImage(resized_image, master=label)
            label.configure(image=thumbnail, height=img_height)
            label.image = thumbnail
        label.pack(fill='x')

        panel = Frame(self, width=100)
        panel.grid_columnconfigure(1, weight=1)
        Label(panel, text='Title:').grid(row=0, column=0, sticky=W)
        Entry(panel, textvariable=self.__title_var, width=40).grid(row=0, column=1, sticky=E, pady=(0, 5))
        Label(panel, text='Message:').grid(row=1, column=0, sticky=NW)
        self.__textbox = Text(panel, font=default_font, width=40, height=7)
        self.__textbox.grid(row=1, column=1, sticky=E)
        panel.pack(fill='x', padx=10, pady=10)

        buttons = Frame(self)
        Button(buttons, text='Send', width=12, height=2, command=self.send_report).grid(row=0, column=0, padx=(0, 15))
        Button(buttons, text='Cancel', width=12, height=2, command=self.close_dialog).grid(row=0, column=1)
        buttons.pack(pady=(0, 10))

        # Put dialog in center of parent window
        self.update()
        self.geometry("+%d+%d" % (parent.winfo_rootx() + (parent.winfo_width() - self.winfo_reqwidth()) / 2,
                                  parent.winfo_rooty() + (parent.winfo_height() - self.winfo_reqheight()) / 2))

    def send_report(self):
        self.__title = self.__title_var.get()
        self.__message = self.__textbox.get("1.0", END)

        ErrorReport.send(self.__title, self.__message, utils.logger.log.getvalue(), self.__screenshot)

        # img_bytes = io.BytesIO()
        # self.__screenshot.save(img_bytes, format='PNG')
        #
        # if not config.SERVER_URL:
        #     messagebox.showerror(title='Error', message="Can't send bug report.\r\nSERVER_URL = NULL")
        #     return
        #
        # url = f'{config.SERVER_URL}/report'
        # headers = {
        #     'hash_id': config.LICENSE,
        #     'app_id': config.APP_ID
        # }
        # data = {
        #     'title': self.__title,
        #     'message': self.__message,
        # }
        # files = {
        #     'screenshot': ('image_file', img_bytes.getvalue(), 'image/png'),
        #     'log': ('log_file', utils.logger.log.getvalue(), 'text/plain')
        # }
        # with requests.post(url, headers=headers, data=data, files=files) as resp:
        #     if resp.status_code == 200:
        #         messagebox.showinfo(title='Info', message="Your report has been successfully submitted.\n"
        #                                                   "We will fix the problem as soon as possible.\n"
        #                                                   "Still need help? Join our discord.")
        #     else:
        #         messagebox.showerror(title='Submit error',
        #                              message=f'Unable to submit report. HTTP Status code: {resp.status_code}')
        self.close_dialog()


class ReportButton(Button):
    __report_icon: ImageTk
    _root: Tk
    __l2window: L2Window
    __get_current_l2client = None

    def open_report_dialog(self):
        self.__l2window = self.__get_current_l2client()
        if self.__l2window:
            screenshot = self.__l2window.screenshot
            if screenshot:
                dlg = ReportDialog(self._root, screenshot)
                self._root.wait_window(dlg)
            else:
                l2helper.msg_box(
                    f'ERROR: Can\'t send bug report.\r\nLineage 2 client window is minimized.\r\nPlease restore Lineage window.',
                    config.APP_NAME, l2helper.MB_ICONERROR)

    def __init__(self, master, root, get_current_l2client):
        super().__init__(master, text="Report", image=Icons.warning, compound=TOP, borderwidth=0, fg="red",
                         cursor="hand2", command=self.open_report_dialog)
        self._root = root
        self.__get_current_l2client = get_current_l2client

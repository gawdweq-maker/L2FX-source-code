from tkinter import Tk, LabelFrame, Frame, Label, StringVar, Button, Radiobutton, IntVar

from f_clicker.Action import Action
from f_clicker.KeyRepeater import KeyRepeater
from f_clicker_mv.ItemList import ItemList


class ActionsRoster(Frame):
    def __init__(self, master=None, root=None, l2client=None, **kw):
        self.root = root
        self.l2client = l2client
        self.key_repeaters = []
        self.current_key = None
        self.key_it = None
        self.auto_farm = False
        self.hunt_zone = False

        super().__init__(master, **kw)
        self.bind("<Configure>", self.on_resize)

        self.sortable_list = ItemList(master, 40, offset_x=10, offset_y=10, gap=5, item_borderwidth=1, item_relief="groove")
        self.sortable_list.pack(fill='both', padx=0, pady=0)

        for i in range(4):
            item = self.sortable_list.create_item(value=i)
            repeater = Action(item, root=root)
            repeater.pack(side='left')
            item.set_command(repeater)
            self.sortable_list.add_item(item)


    def on_resize(self, event):
        self.sortable_list.on_resize(event)
        # for item in self.sortable_list:
        #     item.resize(event.width)
        # sortable_list.on_resize(event.width)
        # if event.widget == root:
        #     sortable_list.on_resize(event.width)
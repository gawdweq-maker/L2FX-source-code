import enum
import time
from tkinter import IntVar, Frame, Checkbutton, NW, Label, Entry, TclError, DISABLED

from kbdmou import Mouse, Keyboard
from scripts import L2Script, L2Window
from scripts.auto_purchase import Items
from scripts.utils import validate_number


class ShopState(enum.Enum):
    closed = 0
    home = 1
    equipment = 2
    enchantment = 3
    supplies = 4
    misc = 5
    adena_items = 6
    events = 7


class AutoPurchase(L2Script):
    enabled_var: IntVar
    shop_open: bool
    purchase_done: bool = False
    current_item: Items.Item or None

    shopping_list: dict     # constant shopping list of items to buy
    items_to_buy: dict      # current list of items to buy

    def create_properties(self, frame: Frame):
        self.enabled_var = IntVar()
        self.items_to_buy = {}
        self.shopping_list = {
            Items.SAYHA_BLESSING: IntVar(value=1),
            Items.SOUL_SHOT: IntVar(value=2),
            Items.SCROLL_BOOST_ATTACK: IntVar(value=1),
            Items.SCROLL_BOOST_DEFENSE: IntVar(),
            Items.XP_GROWTH_SCROLL: IntVar(),
            Items.SAYHA_STORM_LV3: IntVar(),
            Items.MY_TELEPORT_SCROLL: IntVar()
        }

        checkbox_enabled = Checkbutton(frame,
                                       text="Auto purchase (after death)",
                                       variable=self.enabled_var,
                                       command=self.reset)
        checkbox_enabled.pack(padx=25, pady=10, anchor=NW)
        checkbox_enabled.configure(state=DISABLED)

        props = Frame(frame)

        column = 0
        for item, var in self.shopping_list.items():
            label = Label(props, text=item.name, image=item.icon_tk)
            label.image = item.icon_tk
            label.grid(row=0, column=column)
            label.configure(state=DISABLED)
            vcmd = (frame.register(validate_number))
            entry = Entry(props, textvariable=var, justify='center', width=5, validate='all', validatecommand=(vcmd, '%P'))
            entry.grid(row=1, column=column)
            entry.configure(state=DISABLED)
            column += 1

        props.pack(padx=28, pady=0, anchor=NW)

    def on_account_changed(self, settings):
        pass

    def reset(self):
        if self.enabled_var.get() == 1:
            self.purchase_done = False

            # Convert ordered items to current list
            for item, var in self.shopping_list.items():
                try:
                    amount = var.get()
                    if amount > 0:
                        self.items_to_buy[item] = var.get()
                    elif item in self.items_to_buy:
                        del self.items_to_buy[item]
                except TclError:
                    if item in self.items_to_buy:
                        del self.items_to_buy[item]

            self.current_item = None
            self.shop_open = False

    def pre_run(self, l2window: L2Window) -> bool:
        return False

    def run(self, l2window: L2Window):
        # Do nothing if script is not enabled
        if self.enabled_var.get() == 0:
            return

        # is nothing to buy
        if len(self.items_to_buy) == 0:
            self.enabled_var.set(0)
            return

        # is L shop opened?
        shop_state: ShopState = self.get_shop_state(l2window)
        print(shop_state)

        # if shop already opened - then close it!
        if shop_state is not ShopState.closed and self.shop_open is False:
            l2window.activate()
            Keyboard.input(b'<esc>', b'<esc>')
            return

        # if shop is closed - then open L shop!
        if shop_state == ShopState.closed:
            if l2window.click_on_image("scripts\\auto_purchase\\img\\btn_L_coin_shop.png", confidence=.9):
                self.shop_open = True
                return

        # if shop is not Supplies - then go to supplies
        if shop_state != ShopState.supplies:
            if l2window.click_on_image("scripts\\auto_purchase\\img\\tab_supplies.png", confidence=.9):
                return

        pos = self.find_quantity_input(l2window)
        if pos is not None:
            x, y = pos
            Mouse.click(x, y)
            time.sleep(0.2)

            self.current_item = next(iter(self.items_to_buy))
            amount = self.items_to_buy[self.current_item]
            amount_str = str(amount).encode()

            Keyboard.input(b'<backspace>', amount_str, b'<enter>')
            if l2window.click_on_image("scripts\\auto_purchase\\img\\btn_buy.png", confidence=.95):
                time.sleep(0.2)
                # second click to confirm purchase
                l2window.click_on_image("scripts\\auto_purchase\\img\\btn_buy.png", confidence=.95)
            return

        # accept deal results
        if l2window.click_on_image("scripts\\auto_purchase\\img\\btn_accept.png", confidence=.8):
            del self.items_to_buy[self.current_item]
            self.current_item = None

            # close shop if done
            if len(self.items_to_buy) == 0:
                Keyboard.input(b'<esc>', b'<esc>')
                self.purchase_done = True
            return

        # choose next item to buy if exist
        item = next(iter(self.items_to_buy))
        if item is not None:
            l2window.activate()
            l2window.click_on_image(item.icon, confidence=.95)
            time.sleep(0.3)
            Mouse.double_click()
            return
        return

    @staticmethod
    def find_quantity_input(l2window: L2Window):
        return l2window.locate_center("scripts\\auto_purchase\\img\\input_quantity.png", confidence=.8)

    @staticmethod
    def get_shop_state(l2window: L2Window) -> ShopState:
        if l2window.locate_center("scripts\\auto_purchase\\img\\title_L_coin_shop.png", confidence=.95) is None:
            return ShopState.closed

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_home_active.png", confidence=.95) is not None:
            return ShopState.home

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_equipment_active.png", confidence=.95) is not None:
            return ShopState.equipment

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_enchantment_active.png", confidence=.95) is not None:
            return ShopState.enchantment

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_supplies_active.png", confidence=.95) is not None:
            return ShopState.supplies

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_misc_active.png", confidence=.95) is not None:
            return ShopState.misc

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_adena_items_active.png", confidence=.95) is not None:
            return ShopState.adena_items

        if l2window.locate_center("scripts\\auto_purchase\\img\\tab_events_active.png", confidence=.95) is not None:
            return ShopState.events

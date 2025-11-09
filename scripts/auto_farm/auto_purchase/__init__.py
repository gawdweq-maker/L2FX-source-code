from farm_bot.core.L2Bot import L2Bot
from farm_bot.core.L2Window import L2Window
from scripts import L2Script, FrameComponent, Settings, Properties
from scripts.utils import log


class AutoPurchase(L2Script, FrameComponent):

    def reset(self):
        pass

    def run(self, l2window: L2Window, bot: L2Bot) -> bool:
        log('In town -> purchase consumables', bot=bot)
        return True

    def on_account_changed(self, account: Properties.Account):
        pass

    def on_update_settings(self, settings: Settings):
        pass

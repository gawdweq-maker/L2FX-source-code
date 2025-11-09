from PIL import ImageTk, Image

import l2helper


class Singleton(type):
    _instances = {}
    __stopwatch_icon = None
    __plus_icon = None
    __trash_icon = None
    __discord_icon = None
    __telegram_icon = None
    __cpu_icon = None
    __key_icon = None
    __gear_icon = None
    __play_icon = None
    __stop_icon = None
    __warning_icon = None
    __mouse_icon = None
    __keyboard_icon = None
    __coin_icon = None
    __castle_icon = None
    __party_icon = None
    __drag_icon = None
    __valhalla_icon = None
    __skill_resurrect_icon = None
    __skill_teleport_icon = None
    __unlocker_icon = None
    __action_alert_icon = None
    __energy_icon = None
    __topup_icon = None

    __size = None

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    @property
    def stopwatch(cls):
        if not cls.__stopwatch_icon:
            img = Image.open("view\\img\\stopwatch-48.png")
            img = img.resize(cls.size)
            cls.__stopwatch_icon = ImageTk.PhotoImage(img)
        return cls.__stopwatch_icon

    @property
    def plus(cls):
        if not cls.__plus_icon:
            img = Image.open("view\\img\\plus-48.png")
            img = img.resize(cls.size)
            cls.__plus_icon = ImageTk.PhotoImage(img)
        return cls.__plus_icon

    @property
    def trash(cls):
        if not cls.__trash_icon:
            img = Image.open("view\\img\\trash-48.png")
            img = img.resize(cls.size)
            cls.__trash_icon = ImageTk.PhotoImage(img)
        return cls.__trash_icon

    @property
    def discord(cls):
        if not cls.__discord_icon:
            cls.__discord_icon = ImageTk.PhotoImage(Image.open("view\\img\\discord.png"))
        return cls.__discord_icon

    @property
    def telegram(cls):
        if not cls.__telegram_icon:
            cls.__telegram_icon = ImageTk.PhotoImage(Image.open("view\\img\\telegram.png"))
        return cls.__telegram_icon

    @property
    def cpu(cls):
        if not cls.__cpu_icon:
            cls.__cpu_icon = ImageTk.PhotoImage(Image.open("view\\img\\cpu.png"))
        return cls.__cpu_icon

    @property
    def key(cls):
        if not cls.__key_icon:
            cls.__key_icon = ImageTk.PhotoImage(Image.open("view\\img\\key.png"))
        return cls.__key_icon

    @property
    def gear(cls):
        if not cls.__gear_icon:
            img = Image.open("view\\img\\gear-48.png")
            img = img.resize(cls.size)
            cls.__gear_icon = ImageTk.PhotoImage(img)
        return cls.__gear_icon

    @property
    def play(cls):
        if not cls.__play_icon:
            img = Image.open("view\\img\\play-48.png")
            img = img.resize(cls.size)
            cls.__play_icon = ImageTk.PhotoImage(img)
        return cls.__play_icon

    @property
    def stop(cls):
        if not cls.__stop_icon:
            img = Image.open("view\\img\\stop-48.png")
            img = img.resize(cls.size)
            cls.__stop_icon = ImageTk.PhotoImage(img)
        return cls.__stop_icon

    @property
    def warning(cls):
        if not cls.__warning_icon:
            img = Image.open("view\\img\\warning-48.png")
            img = img.resize(cls.size)
            cls.__warning_icon = ImageTk.PhotoImage(img)
        return cls.__warning_icon

    @property
    def mouse(cls):
        if not cls.__mouse_icon:
            img = Image.open("view\\img\\mouse-48.png")
            img = img.resize(cls.size)
            cls.__mouse_icon = ImageTk.PhotoImage(img)
        return cls.__mouse_icon

    @property
    def keyboard(cls):
        if not cls.__keyboard_icon:
            img = Image.open("view\\img\\keyboard-48.png")
            img = img.resize(cls.size)
            cls.__keyboard_icon = ImageTk.PhotoImage(img)
        return cls.__keyboard_icon

    @property
    def coin(cls):
        if not cls.__coin_icon:
            img = Image.open("view\\img\\coin-48.png")
            img = img.resize(cls.size)
            cls.__coin_icon = ImageTk.PhotoImage(img)
        return cls.__coin_icon

    @property
    def castle(cls):
        if not cls.__castle_icon:
            img = Image.open("view\\img\\castle-48.png")
            img = img.resize(cls.size)
            cls.__castle_icon = ImageTk.PhotoImage(img)
        return cls.__castle_icon

    @property
    def party(cls):
        if not cls.__party_icon:
            img = Image.open("view\\img\\party-38.png")
            img = img.resize(cls.size)
            cls.__party_icon = ImageTk.PhotoImage(img)
        return cls.__party_icon

    @property
    def drag(cls):
        if not cls.__drag_icon:
            img = Image.open("view\\img\\drag.png")
            cls.__drag_icon = ImageTk.PhotoImage(img)
        return cls.__drag_icon

    @property
    def valhalla(cls):
        if not cls.__valhalla_icon:
            img = Image.open("view\\img\\valhalla2.png")
            img = img.resize(cls.size)
            cls.__valhalla_icon = ImageTk.PhotoImage(img)
        return cls.__valhalla_icon

    @property
    def skill_resurrect(cls):
        if not cls.__skill_resurrect_icon:
            img = Image.open("view\\img\\skill-res-38.png")
            img = img.resize(cls.size)
            cls.__skill_resurrect_icon = ImageTk.PhotoImage(img)
        return cls.__skill_resurrect_icon

    @property
    def skill_teleport(cls):
        if not cls.__skill_teleport_icon:
            img = Image.open("view\\img\\skill-teleport-38.png")
            img = img.resize(cls.size)
            cls.__skill_teleport_icon = ImageTk.PhotoImage(img)
        return cls.__skill_teleport_icon

    @property
    def unlocker(cls):
        if not cls.__unlocker_icon:
            img = Image.open("view\\img\\unlocker-38.png")
            img = img.resize(cls.size)
            cls.__unlocker_icon = ImageTk.PhotoImage(img)
        return cls.__unlocker_icon

    @property
    def action_alert(cls):
        if not cls.__action_alert_icon:
            img = Image.open("view\\img\\action-alert-38.png")
            img = img.resize(cls.size)
            cls.__action_alert_icon = ImageTk.PhotoImage(img)
        return cls.__action_alert_icon

    @property
    def energy(cls):
        if not cls.__energy_icon:
            img = Image.open("view\\img\\energy-28.png")
            # img = img.resize(cls.size)
            cls.__energy_icon = ImageTk.PhotoImage(img)
        return cls.__energy_icon

    @property
    def topup(cls):
        if not cls.__topup_icon:
            img = Image.open("view\\img\\topup.png")
            img = img.resize(cls.size)
            cls.__topup_icon = ImageTk.PhotoImage(img)
        return cls.__topup_icon

    @property
    def size(cls):
        if not cls.__size:
            scale = l2helper.get_windows_screen_scaling()
            width_height = int(24 * scale)
            cls.__size = (width_height, width_height)
        return cls.__size


class Icons(metaclass=Singleton):
    pass

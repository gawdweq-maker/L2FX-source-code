from enum import Enum


class AppType(Enum):
    L2FX = 1
    TEZ = 2


class LicenseType(Enum):
    Basic = (1, "Basic")
    Premium = (2, "Premium")
    BetaTest = (3, "Beta Test")

    def __init__(self, num, label):
        self._num = num
        self._label = label

    @property
    def label(self):
        return self._label

    @classmethod
    def from_string(cls, name):
        for member in cls:
            if member.label == name:
                return member
        return None

import random

from core.grid import CellType


class Stone:
    def __init__(self, index, hp):
        self.index = index
        self.hp = hp  # 剩余被消除次数

    def __repr__(self) -> str:
        return 'stone: index=' + str(self.index) + ' hp=' + str(self.hp)

    @staticmethod
    def random_hp():
        return int(random.random() * 7 + 1)

    @staticmethod
    def get_type():
        return CellType.STONE

    def show(self) -> str:
        return '[__' + str(self.hp) + '__]'

    def simple_show(self) -> str:
        return self.hp

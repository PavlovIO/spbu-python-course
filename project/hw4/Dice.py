from random import randint

class DiceManager():
    def __init__(self) -> None:
        self.dices: list[int] = [1,1,1,1,1]
        self.locked: list[int] = []

    def lock(self, dice_id: list[int]) -> None:
        self.locked = dice_id

    def roll(self) -> None:
        for id in range(5):
            if id not in self.locked:
                self.dices[id] = randint(1, 6)

    def get_dices(self) -> list[int]:
        return self.dices.copy()
    def get_locked(self) -> list[int]:
        return self.locked.copy()



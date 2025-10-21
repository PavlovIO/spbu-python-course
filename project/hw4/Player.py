from .Dice import DiceManager
from .Score import ScoreManager

class PlayerManager():
    def __init__(self, dm: DiceManager, name: str = "Anonim") -> None:
        self.name = name
        self.dm = dm
        self.score = ScoreManager()
        self.rolls = 0
        self.calculated: dict[str, int] = {}

    def start_round(self) -> None:
        self.rolls = 0

    def roll_dices(self) -> None:
        self.dm.roll()
        self.calculated = self.calculate()
        self.rolls += 1

    def choose_comb(self, comb: str) -> None:
        self.score.add_comb(comb, self.calculated[comb])

    def calculate(self):
        roll_mult = 2 if self.rolls == 1 else 1

        available = self.score.get_available()
        dices = self.dm.get_dices()
        calculated = {}
        
        for comb in available:
            c = 0
            if comb == "chance":
                c = sum(dices)
            elif comb == "aces":
                c = dices.count(1) * 1 * roll_mult
            elif comb == "twos":
                c = dices.count(2) * 2 * roll_mult
            elif comb == "threes":
                c = dices.count(3) * 3 * roll_mult
            elif comb == "fours":
                c = dices.count(4) * 4 * roll_mult
            elif comb == "fives":
                c = dices.count(5) * 5 * roll_mult
            elif comb == "sixes":
                c = dices.count(6) * 6 * roll_mult
            elif comb == "pair":
                for number in set(dices):
                    if dices.count(number) >= 2: 
                        c = max(c, number * 2) * roll_mult
            elif comb == "two_pairs":
                possible = []
                for number in set(dices):
                    if dices.count(number) >= 2: 
                        possible.append(number)
                if len(possible) >= 2:
                    c = sum(sorted(possible)[-2:]) * roll_mult
            elif comb == "3_of_a_kind":
                for number in set(dices):
                    if dices.count(number) >= 3: 
                        c = max(c, number * 3) * roll_mult
            elif comb == "low_straight":
                if all([i in set(dices) for i in [1,2,3,4]]):
                    c = 10 * roll_mult
                elif all([i in set(dices) for i in [2,3,4,5]]):
                    c = 14 * roll_mult
            elif comb == "high_straight":
                if all([i in set(dices) for i in [1,2,3,4,5]]):
                    c = 15 * roll_mult
                elif all([i in set(dices) for i in [2,3,4,5,6]]):
                    c = 20 * roll_mult
            elif comb == "odd":
                if all([i%2==0 for i in dices]):
                    c = sum(dices) * roll_mult
            elif comb == "even":
                if all([i%2==1 for i in dices]):
                    c = sum(dices) * roll_mult
            elif comb == "full_house":
                counts = sorted([dices.count(i) for i in set(dices)])
                if counts == [2,3]:
                    c = sum(dices) * roll_mult
            elif comb == "4_of_a_kind":
                for number in set(dices):
                    if dices.count(number) >= 4: c = max(c, number * 4) * roll_mult
            elif comb == "YAHTZEE":
                if len(set(dices)) == 1:
                    c = sum(dices) * roll_mult + 50
            else:
                raise ValueError(f"No such {comb} combination")
            calculated[comb] = c
        return calculated


                    


from typing import Union
from .DiceManager import DiceManager
from .ScoreManager import ScoreManager

"""
Player can roll dices, lock any, choose a combination, start/end round, view score table
"""

class PlayerManager():
    def __init__(self, dm: DiceManager, name: str) -> None:
        self.name = name
        self.dm = dm
        self.score = ScoreManager()
        self.rolls = 0
        self.calculated: dict[str, int] = {}

    def start_round(self) -> None:
        self.rolls = 0

    def lock_dices(self, dice_ids: list[int]) -> None:
        self.dm.lock(dice_ids)

    def roll_dices(self, round:int = 2) -> None:
        self.dm.roll()
        self.rolls += 1
        self.calculated = self.calculate(round=round)


    def choose_comb(self, comb: str) -> None:
        self.score.add_comb(comb, self.calculated[comb])
        # maybe add flag for end of the round

    def get_score(self) -> dict[str,list[Union[int,bool]]]:
        return self.score.table
    
    def get_calculated(self) -> dict[str, int]:
        calc: dict[str, int] = self.calculated.copy()
        for key in self.get_score().keys():
            if key not in calc.keys():
                calc[key] = 0
        return calc

    def calculate(self, round:int = 2) -> dict[str, int]:
        dices = self.dm.get_dices()
        calculated: dict[str, int] = {}
        if round == 1:
            available = ["aces", "twos", "threes", "fours", "fives", "sixes"]
        else:
            roll_mult = 2 if self.rolls == 1 else 1
            available = self.score.get_available()
        
        for comb in available:
            c = 0
            if comb == "chance":
                c = sum(dices)
            elif comb == "aces":
                c = dices.count(1) - 3
            elif comb == "twos":
                c = dices.count(2) - 3
            elif comb == "threes":
                c = dices.count(3) - 3
            elif comb == "fours":
                c = dices.count(4) - 3
            elif comb == "fives":
                c = dices.count(5) - 3
            elif comb == "sixes":
                c = dices.count(6) - 3
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
    
    def fin_round_1(self, chosen_comb: str) -> None:
        if chosen_comb not in ["aces", "twos", "threes", "fours", "fives", "sixes"]:
            raise ValueError("Round 1 choice must be an upper section combination")
        self.score.calc_bonus()

        

                    


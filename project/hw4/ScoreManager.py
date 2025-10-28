from .modules import *
"""
Score table: you can get bonus, choose the combination, find available, get total
"""

class ScoreManager():
    def __init__(self) -> None:
        self.table: dict[str, list[Union[int, bool]]] = {
            #upper section
            "aces" : [0, False],
            "twos" : [0, False],
            "threes" : [0, False],
            "fours" : [0, False],
            "fives" : [0, False],
            "sixes" : [0, False],
            #lower section
            "bonus" : [0, False],
            "pair" : [0, False],
            "two_pairs" : [0, False],
            "3_of_a_kind" : [0, False],
            "low_straight" : [0, False],
            "high_straight" : [0, False],
            "odd" : [0, False],
            "even" : [0, False],
            "full_house" : [0, False],
            "4_of_a_kind" : [0, False],
            "chance" : [0, False],
            "YAHTZEE" : [0, False]
        }

    _R1KEYS = ["aces","twos","threes","fours","fives","sixes"]
    _R2KEYS = ["bonus","pair","two_pairs","3_of_a_kind","low_straight","high_straight","odd","even","full_house","4_of_a_kind","chance","YAHTZEE"]

    def calc_bonus(self) -> None:
        s = 0
        for key in self._R1KEYS:
            s += self.table[key][0]
            self.table[key][1] = True
        if s > 0 : 
            s = 50
        else : 
            s = 0
        self.table["bonus"] = [s, True]

    def get_available(self, round: int = 2) -> list[str]:
        if round == 2: 
            keys = self._R2KEYS
        elif round == 1: 
            keys = self._R1KEYS
        else: 
            raise ValueError(f"Expected round is 1 or 2 but got {round}")
        
        available = []
        for key in keys:
            if not self.table[key][1]:
                available.append(key)
        return available

    def add_comb(self, name: str, points: int) -> None:
        if name in self.table.keys():
            if not self.table[name][1]:
                self.table[name][0] = points
                self.table[name][1] = True
            else: 
                raise ValueError(f"Can't add points to {name} combination as it is already set")
        else:
            raise ValueError(f"No such {name} combination")

    def total_score(self) -> int:
        s = 0
        keys = self._R2KEYS
        for key in keys:
            s += self.table[key][0]
        return s
    
    def _set_score(self, new_score: dict[str, int]):
        for key, point in new_score.items():
            if key not in self.table.keys(): 
                raise ValueError(f"No {key} combination in the score table")
            self.table[key] = [point, True]
        


from typing import Union

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

    def get_available(self) -> list[str]:
        available = []
        for key, item in self.table.items():
            if not item[1]:
                available.append(key)
        return available

    def add_comb(self, name: str, points: int) -> None:
        if name in self.table.keys():
            if not self.table[name][1]:
                self.table[name][0] = points
            else: 
                raise ValueError(f"Can't add points to {name} combination as it is already set")
        else:
            raise ValueError(f"No such {name} combination")
        
    def upper_sum(self) -> int:
        s = 0
        for key in ("aces","twos","threes","fours","fives","sixes"):
            s += self.table[key][0]
        return s
    
    def total_score(self) -> int:
        s = 0
        for _, item in self.table.items():
            s += item[0]
        s += 0 if self.upper_sum() < 63 else 35
        return s
    
        

    
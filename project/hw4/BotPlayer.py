from .PlayerManager import *
from .modules import *

class BotPlayer(PlayerManager):
    def __init__(self, dm: DiceManager, name: str, strategy: str):
        super().__init__(dm, name, is_bot=True)
        if strategy not in ["smart","safe","full_gamba"]:
            raise ValueError(f"Unknown strategy {strategy}")
        self.strategy = strategy
    
    def decide_lock(self, dices: list[int], round: int) -> list[int]:
        if round == 1:
            dice_amount = {dice: dices.count(dice) for dice in set(dices)}
            target = 1
            target_freq = 0
            for dice, freq in dice_amount.items():
                target = dice if freq >= target_freq else target
                target_freq = max(freq, target_freq)
            return [i for i in range(5) if dices[i]==target]
        
        if self.strategy == "safe":
            available = list(self.calculate().keys())
            dices_set = set(dices)
            #check for potential straight
            low_targets = [{1,2,3,4}, {2,3,4,5},{3,4,5,6}]
            high_targets = [{1,2,3,4,5}, {2,3,4,5,6}]
            can_do_low = any(len(tar - dices_set) == 1 for tar in low_targets)
            can_do_high = any(len(tar - dices_set) == 1 for tar in high_targets)

            if "low_straight" not in available:
                can_do_low = False
            if "high_straight" not in available:
                can_do_high = False
            have_pairs = True
            #dice counter
            if "pair" in available or \
                "two_pairs" in available or \
                "3_of_a_kind" in available or \
                "4_of_a_kind" in available or \
                "full_house" in available or \
                "YAHTZEE" in available:
                have_pairs = False
            counts:dict[int, int] = {}
            for d in dices:
                counts[d] = counts.get(d, 0) + 1
            max_count = max(counts.values())
            best_group_value = max(k for k, v in counts.items() if v == max_count)

            straight_potential = max(
                [11 + i*4 for i in range(3)] if can_do_low else [0] +\
                [15 + i*5 for i in range(2)] if can_do_high else [0]
            )
            group_potential = best_group_value * max_count if max_count >= 2 else 0

            if straight_potential > group_potential:
                if can_do_high:
                    for tar in [{2,3,4,5,6}, {1,2,3,4,5}]:
                        if len(tar - dices_set) == 1:
                            locked = []
                            used = set()
                            for i in range(len(dices)):
                                if dices[i] in tar and dices[i] not in used:
                                    locked.append(i)
                                    used.add(dices[i])
                            return locked
                if can_do_low:
                    for tar in [{2,3,4,5}, {1,2,3,4}]:
                        if len(tar - dices_set) == 1:
                            locked = []
                            used = set()
                            for i in range(len(dices)):
                                if dices[i] in tar and dices[i] not in used:
                                    locked.append(i)
                                    used.add(dices[i])
                            return locked

            if max_count >= 2 and have_pairs:
                return [i for i, d in enumerate(dices) if d == best_group_value]
            return []
        
        elif self.strategy == "full_gamba":
            counts = {}
            for d in dices:
                counts[d] = counts.get(d, 0) + 1
            max_count = max(counts.values())
            most_common = max(k for k, v in counts.items() if v == max_count)

            dices_set = set(dices)
            if max_count >= 4:
                return [i for i, d in enumerate(dices) if d == most_common]

            sequences = [[1,2,3,4], [2,3,4,5], [3,4,5,6], [1,2,3,4,5], [2,3,4,5,6]]
            best_seq = []
            best_overlap = 0
            for seq in sequences:
                overlap = len(set(seq) & dices_set)
                if overlap > best_overlap and overlap >= 3:
                    best_overlap = overlap
                    best_seq = seq

            if best_overlap >= 4:
                locked = []
                used = set()
                for i in range(len(dices)):
                    if dices[i] in best_seq and dices[i] not in used:
                        locked.append(i)
                        used.add(dices[i])
                return locked

            if max_count == 3:
                return [i for i in range(len(dices)) if dices[i] == most_common]

            return []

        elif self.strategy == "smart":
            current_dices = self.dm.get_dices()
            available_combs = self.score.get_available(round=round)
            if not available_combs:
                return []

            roll_mult = 1

            def simulate_calculate(dices, available, mult):
                calc = {}
                for comb in available:
                    c = 0
                    if comb == "chance":
                        c = sum(dices)
                    elif comb == "pair":
                        for number in set(dices):
                            if dices.count(number) >= 2:
                                c = max(c, number * 2) * mult
                    elif comb == "two_pairs":
                        possible = []
                        for number in set(dices):
                            if dices.count(number) >= 2:
                                possible.append(number * 2)
                        if len(possible) >= 2:
                            c = sum(sorted(possible)[-2:]) * mult
                    elif comb == "3_of_a_kind":
                        for number in set(dices):
                            if dices.count(number) >= 3:
                                c = max(c, number * 3) * mult
                    elif comb == "low_straight":
                        if all(i in set(dices) for i in [1,2,3,4]):
                            c = 10 * mult
                        elif all(i in set(dices) for i in [2,3,4,5]):
                            c = 14 * mult
                    elif comb == "high_straight":
                        if all(i in set(dices) for i in [1,2,3,4,5]):
                            c = 15 * mult
                        elif all(i in set(dices) for i in [2,3,4,5,6]):
                            c = 20 * mult
                    elif comb == "odd":
                        if all(i % 2 == 0 for i in dices):
                            c = sum(dices) * mult
                    elif comb == "even":
                        if all(i % 2 == 1 for i in dices):
                            c = sum(dices) * mult
                    elif comb == "full_house":
                        counts_vals = sorted([dices.count(i) for i in set(dices)])
                        if counts_vals == [2, 3]:
                            c = sum(dices) * mult
                    elif comb == "4_of_a_kind":
                        for number in set(dices):
                            if dices.count(number) >= 4:
                                c = max(c, number * 4) * mult
                    elif comb == "YAHTZEE":
                        if len(set(dices)) == 1:
                            c = sum(dices) * mult + 50
                    else:
                        continue
                    calc[comb] = c
                return calc

            all_lock_options = [list(combo) for r in range(6) for combo in combinations(range(5), r)]

            best_lock = []
            best_expectation = -1.0
            SIM_COUNT = 200

            for lock_option in all_lock_options:
                total_score = 0
                valid_sim = 0

                for _ in range(SIM_COUNT):
                    sim_dices = current_dices.copy()
                    for i in range(5):
                        if i not in lock_option:
                            sim_dices[i] = randint(1, 6)

                    simulated_calc = simulate_calculate(sim_dices, available_combs, roll_mult)
                    best_sim_score = max((simulated_calc.get(c, -999) for c in available_combs), default=-999)

                    if best_sim_score > -999:
                        total_score += best_sim_score
                        valid_sim += 1

                expectation = total_score / valid_sim if valid_sim else -999
                if expectation > best_expectation:
                    best_expectation = expectation
                    best_lock = lock_option

            return best_lock
        
        return []

    def decide_choose(self, round: int) -> str:
        available = self.score.get_available(round=round)
        if round == 1:
            best = max(available, key=lambda c: self.calculated.get(c, 0))
            return best
        
        if self.strategy == "full_gamba":
            valid_choices = [(self.calculated.get(c, 0), c) for c in available if self.calculated.get(c, -1) >= 0]
            if valid_choices:                
                targ_comb = valid_choices[0]
                for val, com  in valid_choices:
                    if val >= targ_comb[0]: targ_comb = (val, com)
                return targ_comb[1]
            return max(available, key=lambda c: self.calculated.get(c, 0))
        
        elif self.strategy == "safe":
            reliable = {"pair", "two_pairs", "3_of_a_kind", "4_of_a_kind", "full_house", "chance", "YAHTZEE"}
            candidates: list[tuple[int, str]] = []
            for comb in available:
                score = self.calculated.get(comb, 0)
                if score <= 0:
                    continue
                if comb in reliable or comb in ["low_straight", "high_straight"]:
                    candidates.append((score, comb))
            if candidates:
                targ_comb_safe: tuple[int, str] = candidates[0]
                for val, com  in candidates: 
                    if val >= targ_comb_safe[0]: targ_comb_safe = (val, com)
                return targ_comb_safe[1]
            return max(available, key=lambda c: self.calculated.get(c,0))
        
        elif self.strategy == "smart":
            return max(available, key=lambda c: self.calculated.get(c, 0))
        return available[0]
    
    def _lock_for_comb(self, comb: str, dices: list[int]) -> list[int]:
        if comb == "pair":
            for num in range(6, 0, -1):
                if dices.count(num) >= 2:
                    return [i for i in range(5) if dices[i]==num]
        elif comb == "3_of_a_kind" or comb == "4_of_a_kind":
            kind = 3 if "3" in comb else 4
            for num in range(6, 0, -1):
                if dices.count(num) >= kind:
                    return [i for i in range(5) if dices[i]==num]
        elif comb == "full_house":
            counts: dict[int, int] = {}
            for d in dices:
                counts[d] = counts.get(d, 0) + 1
            if sorted(counts.values()) == [2, 3]:
                return list(range(5))  # lock everything
        elif "low_straight" == comb:
            if len(set(dices)) >= 4:
                straight = self.low_straigh_check(dices)
                if straight:
                    locked_ss: list[int] = []
                    for i in range(5):
                        if (dices[i] in straight) and (not dices[i] in locked_ss):
                            locked_ss.append(dices[i])
                    return locked_ss
        elif "high_straight" == comb:
            if len(set(dices)) == 5:
                straight = self.high_straigh_check(dices)
                if straight:
                    locked_hs: list[int] = []
                    for i in range(5):
                        if (dices[i] in straight) and (not dices[i] in locked_hs):
                            locked_hs.append(dices[i])
                    return locked_hs
        elif comb == "odd":
            locked = [i for i in range(5) if i%2==0]
            return locked
        elif comb == "even":
            locked = [i for i in range(5) if i%2==1]
            return locked
        elif comb == "YAHTZEE":
            if len(set(dices)) == 1:
                return list(range(5))
            # иначе — лочим самый частый
            counts = {dice: dices.count(dice) for dice in set(dices)}
            target = 1
            target_freq = 0
            for dice, freq in counts.items():
                target = dice if freq >= target_freq else target
                target_freq = max(freq, target_freq)
            return [i for i, d in enumerate(dices) if d == target]
        return []
    
    def low_straigh_check(self, dices: list[int]) -> list[int]:
        needed = [[3,4,5,6],[2,3,4,5],[1,2,3,4]]
        uniq = set(dices)
        for ls in needed:
            if all([i in uniq for i in ls]):
                return ls
        return []
    def high_straigh_check(self, dices: list[int]) -> list[int]:
        needed = [[2,3,4,5,6],[1,2,3,4,5]]
        uniq = set(dices)
        for ls in needed:
            if all([i in uniq for i in ls]):
                return ls
        return []
        
            
    
from .PlayerManager import PlayerManager
from .DiceManager import DiceManager
from .UIManager import UIManager
from random import seed

class GameManager:
    def __init__(self, player_names: list[str], _seed: int | None = None):
        self.players: list[PlayerManager] = []
        self.ui = UIManager()
        self.dm = DiceManager()
        for name in player_names:
            player = PlayerManager(self.dm, name)
            self.players.append(player)
        self.current_player_index = 0
        self.round = 1
        self._seed = _seed
        seed(_seed)

    def play(self) -> None:
        while True:
            self.init_players()
            players_names = [player.name for player in self.players]
            self.ui.write(f"Lets greet players: {str(players_names)}")
            # === ROUND 1: Each player gets ONE turn with up to 3 rolls, chooses ONE upper comb ===
            self.ui.write("=== ROUND 1: Choose ONE upper combination in up to 3 rolls ===")
            for player in self.players:
                self._play_turn(player, round=1)

            # === Round 2: Each player must fill every one of 12 combinations === 
            self.round = 2
            self.ui.write("=== ROUND 2 ===")
            for _ in range(12):
                for player in self.players:
                    self._play_turn(player, round=2)

            self._show_final_scores()

            self.ui.write("Do you want to play again?")
            again = self.ui.get_input(["Y","N"])
            if again == "N":
                self.ui.write("Thanks for playing")
                break

    def init_players(self) -> None:
        self.ui.write("How many players:")
        players_amount = [int(x) for x in self.ui.get_input(["1","2","3","4","5","6"])][0]
        for i in range(1,players_amount+1):
            self.ui.write(f"Player's {i} name is ", _end="")
            name = self.ui.get_raw_input()
            self.players.append(PlayerManager(dm=self.dm,name=name))

    def _play_turn(self, player: PlayerManager, round: int) -> None:
        self.ui.write(f"\n--- {player.name}'s ROUND {round} turn ---")
        player.start_round()
        self.dm.lock([])
        player.roll_dices(round=round)

        for roll_num in range(1, 3):
            self.ui.write(f"Dices: {player.dm.get_dices()}")
            calculated = player.get_calculated()

            available_combs = player.score.get_available(round=round)
            if not available_combs:
                break

            if round ==1:
                self.ui.write("Upper section options:")
                for comb in available_combs:
                    self.ui.write(f"  {comb}: {calculated[comb]}")
            else:
                score_table = player.get_score()
                table_str = self.ui.draw_table(score_table, calculated)
                self.ui.write(table_str)
            
            choice = self.ui.get_input(["lock", "choose", "roll"])[0]

            if choice == "lock":
                dice_ids_str = self.ui.get_input(["1","2","3","4","5","None"], lock=True)
                if "None" in dice_ids_str:
                    dice_ids = []
                else:
                    dice_ids = [int(x)-1 for x in dice_ids_str]
                player.lock_dices(dice_ids)
                player.roll_dices(round=round)
            elif choice == "choose":
                comb = self.ui.get_input(available_combs)[0]
                player.choose_comb(comb)
                return
            elif choice == "roll":
                player.roll_dices(round=round)
                continue

        self.ui.write("Final roll! You must choose a combination.")
        self.ui.write(f"Dices: {player.dm.get_dices()}")

        calculated = player.get_calculated()

        if round == 1:
            self.ui.write("Choose one upper combination:")
            available_upper = player.score.get_available(round=1)
            for comb in available_upper:
                self.ui.write(f"  {comb}: {calculated[comb]}")
        else:
            score_table = player.get_score()
            table_str = self.ui.draw_table(score_table, calculated)
            self.ui.write(table_str)

        available_combs = player.score.get_available(round=round)
        if available_combs:
            comb = self.ui.get_input(available_combs)[0]
            player.choose_comb(comb)
            if round == 1:
                player.fin_round_1(comb)
        else:
            self.ui.write("No combinations left! Skipping turn.")

    def _show_final_scores(self) -> None:
        self.ui.write("\n=== FINAL SCORES ===")
        for player in self.players:
            total = player.score.total_score()
            self.ui.write(f"{player.name}: {total} points")
        # Опционально: определить победителя
        winner = max(self.players, key=lambda p: p.score.total_score())
        self.ui.write(f"\nWinner: {winner.name} with {winner.score.total_score()} points!")
    



            


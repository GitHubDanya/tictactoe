from game import *
from utils import *

class Tournament:
    def __init__(self, game_options: GameOptions = GameOptions()):
        self.game_options = game_options
        self.games = []

        self.stats = {
            "X Wins" : 0,
            "O Wins" : 0,
            "Draws" : 0
        }

        pass

    def start_tournament_loop(self, n: int):
        bar_length = 30

        for i in range(n):
            curr = Game(self.game_options)
            result = curr.run_game_loop()
            self.games.append(curr)

            match result:
                case GameState.X_Won:
                    self.stats["X Wins"] += 1
                case GameState.O_Won:
                    self.stats["O Wins"] += 1
                case _:
                    self.stats["Draws"] += 1

            current_game = i + 1
            percent = (current_game / n) * 100
            filled = int(bar_length * current_game // n)
            bar = "█" * filled + "-" * (bar_length - filled)

            print(
                f"\rProgress: [{bar}] {percent:5.1f}% ({current_game}/{n})",
                end="",
                flush=True,
            )

        print()


    def print_results(self):
        print(self.stats)


    def print_sample(self):
        print(get_string_from_board(self.games[0].board))


    def get_game_at(self, i):
        return self.games[i]
import json
import random
from utils import *

@dataclass
class GameOptions:
    agent_side: Tile = Tile.X
    ai_on: bool = False
    epsilon: float = 0.1
    manual_agent: bool = False
    manual_enemy: bool = False
    tournament_path: str = "tournament.json"
    verbose: bool = False


class Game:
    def __init__(self, options: GameOptions):
        # Init defaults
        self.board = np.full((3, 3), Tile.Empty)
        self.history = []

        # Load options
        self.agent_side = options.agent_side
        self.ai_on = options.ai_on
        self.epsilon = options.epsilon
        self.manual_agent = options.manual_agent
        self.manual_enemy = options.manual_enemy
        self.verbose = options.verbose

        self.tournament_path = options.tournament_path
        with open(self.tournament_path, 'r', encoding='utf-8') as file:
            self.tournament = json.load(file)


    def print_board(self):
        if not self.verbose: return
        print()
        for i in range(3):
            for j in range(3):
                print(f"{self.board[i][j].to_str()}", end=" ")
            print()
        print('-' * 9)


    def get_game_state(self) -> GameState:
        for (player, result) in [(Tile.X, GameState.X_Won), (Tile.O, GameState.O_Won)]:
            won = (
                np.any(np.all(self.board == player, axis=0))
                or np.any(np.all(self.board == player, axis=1))
                or np.all(np.diag(self.board == player))
                or np.all(np.diag(np.fliplr(self.board) == player))
            )

            if won: return result

        if not Tile.Empty in self.board: return GameState.Draw
        else: return GameState.Ongoing


    def get_random_free_coordinate(self) -> tuple[int, int]:
        spaces = get_free_spaces(self.board)
        return random.choice(spaces)


    def ask_user_for_coordinate(self) -> tuple[int, int]:
        decision = int(input("Pick a coordinate (xy, 1-3):  "))
        x = decision % 10
        y = int(decision / 10)

        while x > 3 or y > 3 or self.board[x-1][y-1] != Tile.Empty:
            decision = int(input("Your input is invalid, or the tile is already occupied!\nTry again: "))
            x = int(decision / 10)
            y = decision % 10

        return x-1, y-1


    def get_agent_move(self) -> Move:
        if self.manual_agent:
            x, y = self.ask_user_for_coordinate()
            return Move(x, y, self.agent_side)

        probability = random.random()
        if not self.ai_on or probability < self.epsilon:
            x, y = self.get_random_free_coordinate()
            return Move(x, y, self.agent_side)

        possible_moves = get_possible_moves(get_string_from_board(self.board), self.agent_side)

        matching_tournament_moves = {
            move: self.tournament[move] for move in possible_moves if move in self.tournament
        }
        sort_order = True if self.agent_side == Tile.X else False
        matching_tournament_moves = sorted(
            matching_tournament_moves.items(), key=lambda item: item[1][0], reverse=sort_order
        )

        if len(matching_tournament_moves) <= 0:
            x, y = self.get_random_free_coordinate()
            return Move(x, y, self.agent_side)

        desired_board = matching_tournament_moves[0][0]
        current_board = get_string_from_board(self.board)
        x, y = -1, -1

        for i in range(len(desired_board)):
            if desired_board[i] != current_board[i]:
                x = i // 3
                y = i % 3
                break

        if x < 0 or y < 0:
            raise Exception("Error finding next board!")

        return Move(x, y, self.agent_side)


    def get_enemy_move(self) -> Move:
        if self.manual_enemy:
            x, y = self.ask_user_for_coordinate()
            return Move(x, y, self.agent_side.to_opposing_side())

        x, y = self.get_random_free_coordinate()
        return Move(x, y, self.agent_side.to_opposing_side())


    def play_move(self, move: Move):
        self.board[move.x][move.y] = move.side
        self.history.append(get_string_from_board(self.board))


    def run_game_loop(self) -> GameState:
        while self.get_game_state() == GameState.Ongoing:
            if self.agent_side == Tile.O:
                self.play_move(self.get_enemy_move())
                self.print_board()

                if self.get_game_state() == GameState.Ongoing:
                    self.play_move(self.get_agent_move())

            else:
                self.play_move(self.get_agent_move())
                self.print_board()

                if self.get_game_state() == GameState.Ongoing:
                    self.play_move(self.get_enemy_move())

            self.print_board()

        result = self.get_game_state()

        if self.verbose:
            if result == GameState.Draw:
                print("Draw!")
            elif result.get_winner_tile() == self.agent_side:
                print("Agent won!")
            else:
                print("Agent lost!")

            print(json.dumps(self.history))

        return result
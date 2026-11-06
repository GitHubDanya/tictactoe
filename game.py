import json
import random
from enum import Enum
from dataclasses import field
from utils import *

class LogicType(Enum):
    Random = 0,
    Manual = 1,
    AI = 2

@dataclass
class GameOptions:
    agent_side: Tile = Tile.X
    agent_logic: LogicType = LogicType.AI
    enemy_logic: LogicType = LogicType.Random
    epsilon: float = 0.1
    tournament: dict[str, tuple[float, int]] = field(default_factory=dict)
    uncertainty_score: float = 0.5
    verbose: bool = False


class Game:
    def __init__(self, options: GameOptions):
        # Init defaults
        self.board = np.full((3, 3), Tile.Empty)
        self.history = []

        # Load options
        self.agent_side = options.agent_side
        self.agent_logic = options.agent_logic
        self.enemy_logic = options.enemy_logic
        self.epsilon = options.epsilon
        self.tournament = options.tournament
        self.uncertainty_score = options.uncertainty_score
        self.verbose = options.verbose


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

        if Tile.Empty not in self.board:
            return GameState.Draw
        else:
            return GameState.Ongoing


    def get_random_free_coordinate(self) -> tuple[int, int]:
        spaces = get_free_spaces(self.board)
        return random.choice(spaces)


    def ask_user_for_coordinate(self) -> tuple[int, int]:
        decision = int(input("Pick a coordinate (xy, 1-3):  "))
        x = decision % 10
        y = int(decision / 10)

        while x > 3 or x < 1 or y > 3 or x < 1 or self.board[x-1][y-1] != Tile.Empty:
            decision = int(input("Your input is invalid, or the tile is already occupied!\nTry again: "))
            x = decision % 10
            y = int(decision / 10)

        return x-1, y-1


    def get_greedy_move(self, side: Tile) -> Move:
        possible_boards = get_possible_boards(get_string_from_board(self.board), side)
        scored_possible_boards = {}

        for board in possible_boards:
            if board in self.tournament:
                scored_possible_boards[board] = self.tournament[board]
                continue

            scored_possible_boards[board] = (self.uncertainty_score, 1)

        sort_order = side == Tile.X
        scored_possible_boards = sorted(
            scored_possible_boards.items(), key=lambda item: item[1][0], reverse=sort_order
        )

        if len(scored_possible_boards) <= 0:
            x, y = self.get_random_free_coordinate()
            return Move(x, y, side)

        desired_board = scored_possible_boards[0][0]
        current_board = get_string_from_board(self.board)
        x, y = -1, -1

        for i in range(len(desired_board)):
            if desired_board[i] != current_board[i]:
                x = i // 3
                y = i % 3
                break

        if x < 0 or y < 0:
            raise Exception("Error finding next board!")

        return Move(x, y, side)


    def _get_move(self, logic: LogicType, side) -> Move:
        match logic:
            case LogicType.Manual:
                x, y = self.ask_user_for_coordinate()
            case LogicType.AI if random.random() >= self.epsilon:
                return self.get_greedy_move(side)
            case _:
                x, y = self.get_random_free_coordinate()
        return Move(x, y, side)

    def get_agent_move(self) -> Move:
        return self._get_move(self.agent_logic, self.agent_side)

    def get_enemy_move(self) -> Move:
        return self._get_move(self.enemy_logic, self.agent_side.to_opposing_side())


    def play_move(self, move: Move):
        self.board[move.x][move.y] = move.side
        self.history.append(get_string_from_board(self.board))


    def run_game_loop(self) -> GameState:
        if self.agent_side == Tile.X:
            move_actions = {Tile.X: self.get_agent_move, Tile.O: self.get_enemy_move}
        else:
            move_actions = {Tile.X: self.get_enemy_move, Tile.O: self.get_agent_move}

        current_side = Tile.X

        while self.get_game_state() == GameState.Ongoing:
            get_move_function = move_actions[current_side]

            move = get_move_function()
            self.play_move(move)
            self.print_board()

            current_side = current_side.to_opposing_side()

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
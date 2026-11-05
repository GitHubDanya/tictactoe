import json
import numpy as np
import random
from enum import Enum

class Tile(Enum):
    Empty = 0
    X = 1
    O = 2

    def to_opposing_side(self):
        match self:
            case Tile.X:
                return Tile.O
            case Tile.O:
                return Tile.X
            case _:
                return Tile.Empty

    def to_str(self):
        match self:
            case Tile.X:
                return 'X'
            case Tile.O:
                return 'O'
            case _:
                return ' '

class GameState(Enum):
    Ongoing = 0,
    X_Won = 1,
    O_Won = 2,
    Draw = 3

    def get_winner_tile(self) -> Tile:
        match self:
            case self.X_Won:
                return Tile.X
            case self.O_Won:
                return Tile.O
            case _:
                return Tile.Empty

def get_free_spaces(board: np.ndarray):
    return [tuple(pos) for pos in np.argwhere(board == Tile.Empty)]


def get_string_from_board(board: np.ndarray) -> str:
    res = ""
    for i in range(3):
        for j in range(3):
            res += f"{board[i][j].to_str()}"

    res = res.replace(' ', 'E')
    return res


def get_board_from_string(board_str: str) -> np.ndarray:
    char_to_tile = {
        'E': Tile.Empty,
        ' ': Tile.Empty,
        'X': Tile.X,
        'O': Tile.O
    }

    tiles = [char_to_tile[char] for char in board_str]
    return np.array(tiles, dtype=object).reshape((3, 3))


def get_possible_moves(board: str, side: Tile) -> list[str]:
    res = []

    for i in range(len(board)):
        if board[i] == 'E':
            new_str = board[:i] + side.to_str() + board[i+1:]
            res.append(new_str)

    return res

class GameOptions:
    def __init__(self):
        self.agent_side = Tile.X
        self.ai_on = True
        self.epsilon = 0.1
        self.tournament_path = "tournament.json"
        self.verbose = False

class Game:
    def __init__(self, options: GameOptions):
        # Init defaults
        self.board = np.full((3, 3), Tile.Empty)
        self.history = []

        # Load options
        self.agent_side = options.agent_side
        self.verbose = options.verbose

        # Configure smart guessing
        if options.ai_on:
            self.epsilon = options.epsilon
            self.tournament_path = options.tournament_path
            with open(self.tournament_path, 'r', encoding='utf-8') as file:
                self.tournament = json.load(file)


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


    def get_agent_move(self) -> tuple[int, int]:
        spaces = get_free_spaces(self.board)
        return random.choice(spaces)


    def get_agent_move_manual(self) -> tuple[int, int]:
        decision = int(input("where do i go?? (xy)"))
        x = int(decision / 10)
        y = decision % 10

        while x > 3 or y > 3 or self.board[x-1][y-1] != Tile.Empty:
            decision = int(input("your input is invalid!"))
            x = int(decision / 10)
            y = decision % 10

        return x-1, y-1


    def play_agent_move_random(self):
        agent_x, agent_y = self.get_agent_move()
        self.board[agent_x][agent_y] = self.agent_side
        self.history.append(get_string_from_board(self.board))

    def play_agent_move(self):
        probability = random.random()
        if self.epsilon is None or probability < self.epsilon:
            self.play_agent_move_random()
            return

        possible_moves = get_possible_moves(get_string_from_board(self.board), self.agent_side)
        matching_tournament_moves = {
            move: self.tournament[move] for move in possible_moves if move in self.tournament
        }
        matching_tournament_moves = sorted(
            matching_tournament_moves.items(), key=lambda item: item[1][0], reverse=True
        )

        if len(matching_tournament_moves) <= 0:
            self.play_agent_move_random()
            return

        desired_board = matching_tournament_moves[0][0]
        current_board = get_string_from_board(self.board)
        x, y = -1, -1

        for i in range(len(desired_board)):
            if desired_board[i] != current_board[i]:
                x = i // 3
                y = i % 3
                break

        if x < 0 or y < 0:
            print("Error finding next board!")
            return

        self.board[x][y] = self.agent_side
        self.history.append(get_string_from_board(self.board))



    def get_enemy_move(self) -> tuple[int, int]:
        spaces = get_free_spaces(self.board)
        return random.choice(spaces)


    def play_enemy_move(self):
        enemy_x, enemy_y = self.get_enemy_move()
        self.board[enemy_x][enemy_y] = self.agent_side.to_opposing_side()
        self.history.append(get_string_from_board(self.board))


    def print_board(self):
        if not self.verbose: return
        print()
        for i in range(3):
            for j in range(3):
                print(f"{self.board[i][j].to_str()}", end=" ")
            print()
        print('-' * 9)


    def run_game_loop(self) -> GameState:
        while self.get_game_state() == GameState.Ongoing:
            if self.agent_side == Tile.O:
                self.play_enemy_move()
                self.print_board()
                if self.get_game_state() == GameState.Ongoing: self.play_agent_move()
            else:
                self.play_agent_move()
                self.print_board()
                if self.get_game_state() == GameState.Ongoing: self.play_enemy_move()
            self.print_board()

        result = self.get_game_state()

        if self.verbose:
            if result == GameState.Draw:
                print("Draw!")
            elif result.get_winner_tile() == self.agent_side:
                print("Won!")
            else:
                print("Lost!")

            print(json.dumps(self.history))

        return result


game_options = GameOptions()
game_options.verbose = True
game = Game(game_options)

game.run_game_loop()
import json
from wsgiref.util import request_uri

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


def get_board_from_string(self, board_str: str) -> np.ndarray:
    char_to_tile = {
        'E': Tile.Empty,
        ' ': Tile.Empty,
        'X': Tile.X,
        'O': Tile.O
    }

    tiles = [char_to_tile[char] for char in board_str]
    return np.array(tiles, dtype=object).reshape((3, 3))


class Game:
    def __init__(self, verbose=False):
        self.agent_side = Tile.X
        self.board = np.full((3, 3), Tile.Empty)
        self.history = []
        self.verbose = verbose


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


    def get_enemy_move(self) -> tuple[int, int]:
        spaces = get_free_spaces(self.board)
        return random.choice(spaces)


    def play_agent_move(self):
        agent_x, agent_y = self.get_agent_move()
        self.board[agent_x][agent_y] = self.agent_side
        self.history.append(self.get_board_string())


    def play_enemy_move(self):
        enemy_x, enemy_y = self.get_enemy_move()
        self.board[enemy_x][enemy_y] = self.agent_side.to_opposing_side()
        self.history.append(self.get_board_string())


    def print_board(self):
        if not self.verbose: return
        print()
        for i in range(3):
            for j in range(3):
                print(f"{self.board[i][j].to_str()}", end=" ")
            print()
        print('-' * 9)


    def get_board_string(self) -> str:
        res = ""
        for i in range(3):
            for j in range(3):
                res += f"{self.board[i][j].to_str()}"

        res = res.replace(' ', 'E')
        return res


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


game = Game(verbose=False)

game.run_game_loop()
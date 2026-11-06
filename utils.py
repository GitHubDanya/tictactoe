from dataclasses import dataclass

import numpy as np
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


@dataclass
class Move:
    x: int
    y: int
    side: Tile


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


from tournament import Tournament
from game import Game
from game import GameState

import json


with open("tournament_agent.json", 'r', encoding='utf-8') as file:
    games_dict = json.load(file)

wins = draws = losses = 0

for v in games_dict.values():
    match v[0]:
        case 1: wins += 1
        case 0: draws += 1
        case -1: losses += 1

total = wins+draws+losses
ongoing = len(games_dict) - total

print(f"Total boards: {len(games_dict)}\nWins: {wins}\nDraws: {draws}\nLosses: {losses}\nOngoing: {ongoing}\nTotal: {total}")

filtered_games = {
    k: v for k, v in sorted(games_dict.items(), key=lambda item: item[1][0], reverse=True)
    if v[0] < 1
}
sample = dict(list(filtered_games.items())[:6])
print(sample)

def flip_horizontal(board_str: str) -> str:
    return (
        board_str[2] + board_str[1] + board_str[0] +
        board_str[5] + board_str[4] + board_str[3] +
        board_str[8] + board_str[7] + board_str[6]
    )

def flip_vertical(board_str: str) -> str:
    return board_str[6:9] + board_str[3:6] + board_str[0:3]

symmetrical_matches = {
    board: {
        "value": val,
        "flipped_board": flip_horizontal(board),
        "flipped_value": games_dict[flip_horizontal(board)],
    }
    for board, val in games_dict.items()
    if flip_horizontal(board) in games_dict and flip_horizontal(board) != board
}

sample = list(symmetrical_matches.keys())[:5]

for key in sample:
    print(f"Board: {key}")
    print(f"Details: {symmetrical_matches[key]}\n")

filtered_games = {
    k: v for k, v in sorted(games_dict.items(), key=lambda item: item[1][0], reverse=False)
    if v[0] > -1
}
sample = dict(list(filtered_games.items())[:6])
print(sample)

total_counts = sum(v[1] for k, v in games_dict.items() if 'E' not in k or v[0] in (-1, 1))

print(f'total: {total_counts}')
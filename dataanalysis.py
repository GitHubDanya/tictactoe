
from tournament import Tournament
from game import Game
from game import GameState

import json

tournament = Tournament()
tournament.start_tournament_loop(50)
tournament.print_results()

tournament.print_sample()

# -1 for loss, 1 for victory
gamma = 0.85

def score_game(given_game: Game) -> list[float]:
    final_state = 0
    match given_game.get_game_state():
        case GameState.X_Won:
            final_state = 1
        case GameState.O_Won:
            final_state = -1
        case _:
            final_state = 0

    boards_cnt = len(given_game.history)
    scores = []

    for i in range(boards_cnt):
        score = final_state * pow(gamma, boards_cnt - 1 - i)
        scores.append(score)

    return scores

# tuples structured as (score, n)
games_dict: dict[str, tuple[float, int]] = {}

for game in tournament.games:
    game_boards = game.history
    game_scores = score_game(game)

    for i, board in enumerate(game_boards):
        if board not in games_dict.keys():
            games_dict[board] = (game_scores[i], 1)
        else:
            avg, n = games_dict[board]
            new_avg = (avg * n + game_scores[i]) / (n + 1)
            games_dict[board] = (new_avg, n + 1)

with open("tournament.json", "w") as f:
    json.dump(games_dict, f, indent=2)

len(games_dict)

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

total_counts = sum(v[1] for v in games_dict.values() if v[0] in (-1, 0, 1))
print(f'total: {total_counts}')
print(f'tournament total: {len(tournament.games)}')
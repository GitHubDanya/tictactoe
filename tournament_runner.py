from tournament import *
import json

game_options = GameOptions()
with open("tournament.json", 'r', encoding='utf-8') as file:
    game_options.tournament = json.load(file)

tournament = Tournament(game_options)
tournament.start_tournament_loop(100000)
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

with open("tournament_agent.json", "w") as f:
    json.dump(games_dict, f, indent=2)
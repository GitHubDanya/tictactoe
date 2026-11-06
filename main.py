import matplotlib.pyplot as plt
from tournament import *
from game import *


# tournament = Tournament()
# tournament.start_tournament_loop(100)
# tournament.print_results()
#

game_options = GameOptions()
game_options.agent_side = Tile.X
game_options.enemy_logic = LogicType.Random
game_options.epsilon = 0
with open("tournament.json", 'r', encoding='utf-8') as file:
    game_options.tournament = json.load(file)

results = []
iterations = 50
tournament_games = 200

for i in range(iterations):
    tournament = Tournament(game_options)
    tournament.start_tournament_loop(tournament_games)
    results.append(tournament.stats)

epsilons = range(len(results))
x_wins = [stats["X Wins"] for stats in results]

plt.plot(epsilons, [results[e]["X Wins"] for e in epsilons], label="X Wins", color="red")
plt.plot(epsilons, [results[e]["O Wins"] for e in epsilons], label="O Wins", color="blue")
plt.plot(epsilons, [results[e]["Draws"] for e in epsilons], label="Draws", color="gray")

plt.xlabel("Batch")
plt.ylabel("Count")
plt.title("AI vs Random Matches (Epsilon=0)")
plt.legend()
plt.xticks(epsilons[1::4])

plt.show()

game = Game(game_options)
game.run_game_loop()
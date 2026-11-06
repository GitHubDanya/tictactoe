from tournament import Tournament
from game import *


# tournament = Tournament()
# tournament.start_tournament_loop(100)
# tournament.print_results()
#

game_options = GameOptions()
game_options.verbose = True
game_options.agent_side = Tile.O
game_options.manual_enemy = True
game = Game(game_options)
game.run_game_loop()
import player
from draughtsrules import DraughtsRules
import random


class RandomPlayer(player.Player):
    def get_action(self, current_state, history):
        possible_moves = DraughtsRules.get_all_possible_moves(current_state, self.player_id)

        rand_movelist = random.choice(possible_moves)
        return rand_movelist[0], random.choice(rand_movelist[1])

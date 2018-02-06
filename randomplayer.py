import random

import player
from draughtsrules import DraughtsRules


class RandomPlayer(player.Player):
    def __init__(self, player_id, name=None):
        if name is None:
            name = "Random"

        super(RandomPlayer, self).__init__(player_id, name)

    def get_action(self, current_state, history):
        possible_moves = DraughtsRules.get_all_possible_moves(current_state)

        rand_move = random.choice(possible_moves)
        return player.Move(
            piece=rand_move[0],
            move=random.choice(rand_move[1]),
            request_tie=False
        )

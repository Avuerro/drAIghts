import pygame

from draughtsrules import DraughtsRules


ACTION_RESIGN = 0
ACTION_TIE = 1


class Player:
    def __init__(self, player_id):
        self.player_id = player_id

    def initialize(self):
        pass

    def get_action(self, current_state, history):
        pass

    def end_game(self, history, winner):
        pass

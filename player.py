ACTION_RESIGN = 0
ACTION_TIE = 1


class Player:
    def __init__(self, player_id, name=None):
        self.player_id = player_id

        if name is not None:
            self.name = name
        else:
            self.name = "Player"

    def initialize(self):
        pass

    def get_action(self, current_state, history):
        pass

    def end_game(self, history, winner):
        pass

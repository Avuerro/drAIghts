class Move:
    def __init__(
            self,
            piece=None,
            move=None,
            request_tie=False,
            resign=False,
            accept_tie=False
    ):
        self.piece = piece
        self.move = move
        self.request_tie = request_tie
        self.resign = resign
        self.accept_tie = accept_tie


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

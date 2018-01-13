class Move:
    """An object that holds move information."""

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
    """A player object."""

    def __init__(self, player_id, name=None):
        """Initializes the Player object."""

        self.player_id = player_id

        if name is not None:
            self.name = name
        else:
            self.name = "Player"

    def initialize(self):
        """Initializes members if needed"""

        pass

    def get_action(self, current_state, history):
        """Return a player.Move object that signifies the action to take.

        This method is called every turn for an action to take.

        :param current_state: the current game state (board.GameState)
        :param history: the history of the game so far (board.History)
        """

        pass

    def end_game(self, history, winner):
        """'Clean up' after the game is finished.

        This method is called after the game is finished to allow players
        to perform final actions such as learning.

        :param history: the history of the game (board.History)
        :param winner: the winner of the game. Equal to a playerID (0 or 1)
            or -1 if the game was a draw.
        """

        pass

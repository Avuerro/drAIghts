import player


class ReplayPlayer(player.Player):
    def __init__(self, player_id, movelist, name=None):
        if name is None:
            name = "Replay"

        self.movelist = movelist

        super(ReplayPlayer, self).__init__(player_id, name)

    def get_action(self, current_state, history):
        currentmove = self.movelist.pop(0)

        if currentmove.resigned:
            return player.ACTION_RESIGN
        if currentmove.accepted_tie:
            return player.ACTION_TIE

        return currentmove.piece, currentmove.move, currentmove.proposed_tie

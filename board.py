from copy import deepcopy

import bitarray

from draughtsrules import DraughtsRules


class Piece:
    def __init__(self, pos, is_king):
        self.pos = pos
        self.is_king = is_king

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.pos == other.pos and self.is_king == other.is_king

        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class BoardGrid:
    """Encodes the pieces as a 1 dimensional array.

    Pieces are composed of 3 bits:
        012
        |||
        ||+-> side
        |+--> status
        +---> a piece exists at this location

    """

    def __init__(self, pieces=None):
        if not pieces:
            self._pieces = bitarray.bitarray(
                (
                    "101101101101101"
                    "101101101101101"
                    "101101101101101"
                    "101101101101101"
                    "000000000000000"
                    "000000000000000"
                    "100100100100100"
                    "100100100100100"
                    "100100100100100"
                    "100100100100100"
                )
            )
        else:
            self._pieces = pieces

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            if self._pieces == other._pieces:
                return True

        return False

    def __ne__(self, other):
        return not self == other

    @staticmethod
    def _get_board_index(pos):
        return (10 * pos[1] + pos[0]) // 2 * 3

    def get_pieces(self, player_id):
        """Get the list of pieces for the given player."""

        pieces = []
        for y in range(10):
            for x in range(5):
                board_index = 15 * y + 3 * x
                if self._pieces[board_index] and \
                        self._pieces[board_index + 2] == player_id:
                    square_offset = (board_index // 3 + 1) % 10
                    pieces.append(
                        Piece(
                            (2 * x + (1 <= square_offset <= 5), y),
                            self._pieces[board_index + 1]
                        )
                    )

        return pieces

    def remove_piece(self, pos):
        board_index = self._get_board_index(pos)

        if not self._pieces[board_index]:
            return False

        self._pieces[board_index:board_index + 3] = bitarray.bitarray('000')

        return True

    def move_piece(self, start_pos, end_pos):
        startpos_board_index = self._get_board_index(start_pos)

        if not self._pieces[startpos_board_index]:
            return False

        endpos_board_index = self._get_board_index(end_pos)

        if self._pieces[endpos_board_index]:
            return False

        self._pieces[endpos_board_index] = True
        self._pieces[endpos_board_index + 1] = \
            self._pieces[startpos_board_index + 1]
        self._pieces[endpos_board_index + 2] = \
            self._pieces[startpos_board_index + 2]

        self._pieces[startpos_board_index:startpos_board_index + 3] = \
            bitarray.bitarray('000')

        return True

    def crown_piece(self, pos):
        board_index = self._get_board_index(pos)

        if not self._pieces[board_index]:
            return False

        self._pieces[board_index + 1] = True

        return True

    def get_piece_status(self, pos):
        board_index = self._get_board_index(pos)

        if self._pieces[board_index]:
            return self._pieces[board_index + 1]

        return -1

    def get_piece_player(self, pos):
        board_index = self._get_board_index(pos)

        if self._pieces[board_index]:
            return self._pieces[board_index + 2]

        return -1


NO_TIE_REQUEST = 2
INVALID_TIE_REQUEST = 3


class GameState:
    """A game state object.

    Has the following members:
        - board: the actual board object, stored as a bitarray
        - turn: the current turn
        - current_player: the ID of the current player
        - tie_request: equal to the player ID of the player who requested a tie,
            can otherwise have values NO_TIE_REQUEST or INVALID_TIE_REQUEST
    """

    KING_ROW = (0, 9)

    def __init__(
            self,
            board=None,
            turn=1,
            player=0,
            tie_request=NO_TIE_REQUEST
    ):
        if not board:
            self.board = BoardGrid()
        else:
            self.board = deepcopy(board)

        self.tie_request = tie_request
        self.turn = turn
        self.current_player = player

    def is_opponent_winning(self):
        """Return True if the current game state is a win for the opponent."""

        return not DraughtsRules.get_all_possible_moves(self)

    @staticmethod
    def is_draw(history):
        """Return True if the current game state is a draw."""

        if history.onevs2_moves >= 10:
            return True
        elif history.onevs3_moves >= 32:
            return True
        elif history.consecutive_moves_with_kings >= 50:
            return True
        elif history.gamestates[-1][1] >= 3:
            return True

        return False

    def get_successor(self, piece, move):
        """Get a successor GameState object using a move.

        :param piece: a board.Piece object
        :param move: a list of positions to visit
        """

        possible_moves = DraughtsRules.get_piece_possible_moves(
            piece,
            self.board.get_pieces(self.current_player),
            self.board.get_pieces(not self.current_player),
            self.current_player
        )

        if move not in possible_moves:
            return None

        newstate = GameState(
            board=self.board,
            turn=self.turn if not self.current_player else self.turn + 1,
            player=not self.current_player,
            tie_request=self.tie_request if
            self.tie_request == self.current_player else NO_TIE_REQUEST
        )

        captured_pieces = DraughtsRules.get_captured_pieces(
            piece,
            move,
            self.board.get_pieces(not self.current_player)
        )

        for captured_piece in captured_pieces:
            newstate.board.remove_piece(captured_piece.pos)

        newstate.board.move_piece(piece.pos, move[-1])

        if move[-1][1] == \
                GameState.KING_ROW[newstate.board.get_piece_player(move[-1])]:
            newstate.board.crown_piece(move[-1])

        return newstate


class HistoryMove:
    def __init__(
            self,
            player_id,
            piece=None,
            move=None,
            captured_pieces=False,
            request_tie=False,
            accept_tie=False,
            resign=False
    ):
        self.player_id = player_id
        self.piece = piece
        self.move = move
        self.captured_pieces = captured_pieces
        self.request_tie = request_tie
        self.accepted_tie = accept_tie
        self.resigned = resign


class History:
    """An object that stores past moves.

    Has the following members:
        - movelist: a list of HistoryMove objects
        - gamestates: a list of tuples (GameState, amount_of_times_appeared)
            that stores each past game state.
        - variables that measure when a draw happens
    """

    def __init__(self, initial_state):
        self.movelist = []
        self.gamestates = [(initial_state, 1)]
        self.onevs2_moves = 0  # draw if 10
        self.onevs3_moves = 0  # draw if 32
        self.consecutive_moves_with_kings = 0  # draw if 50

    def get_moves_in_pairs(self):
        index = 0
        while index < len(self.movelist):
            if index + 1 < len(self.movelist) and \
                    self.movelist[index + 1].move:
                yield (self.movelist[index], self.movelist[index + 1])
                index += 1
            elif self.movelist[index].move:
                yield (self.movelist[index],)

            index += 1

    @staticmethod
    def convert_pos_to_index(pos):
        return (10 * pos[1] + pos[0]) // 2 + 1

    def convert_move_to_str(self, move):
        return '{0}{1}{2}'.format(
            self.convert_pos_to_index(move.piece.pos),
            'x' if move.captured_pieces else '-',
            self.convert_pos_to_index(move.move[-1])
        )

    def movelist_as_string(self):
        str_movelist = [
            ' '.join(self.convert_move_to_str(move) for move in moves)
            for moves in self.get_moves_in_pairs()
        ]

        return str_movelist

    def add_move(self, new_gamestate, move, old_gamestate):
        self.movelist.append(move)

        pieces = [
            old_gamestate.board.get_pieces(0),
            old_gamestate.board.get_pieces(1)
        ]

        if move.move:
            for player_index in range(2):
                opponent_index = not player_index

                if len(pieces[player_index]) == 2 \
                        and len(pieces[opponent_index]) == 1 \
                        and any(piece.is_king
                                for piece in pieces[player_index]) \
                        and pieces[opponent_index][0].is_king:
                    self.onevs2_moves += 1
                elif len(pieces[player_index]) == 3 \
                        and len(pieces[opponent_index]) == 1 \
                        and any(piece.is_king
                                for piece in pieces[player_index]) \
                        and pieces[opponent_index][0].is_king:
                    self.onevs3_moves += 1

            if move.piece.is_king and not move.captured_pieces:
                self.consecutive_moves_with_kings += 1
            else:
                self.consecutive_moves_with_kings = 0

        num_gamestate = 1
        for state in self.gamestates:
            if new_gamestate.current_player == state[0].current_player \
                    and new_gamestate.board == state[0].board:
                num_gamestate += 1

        self.gamestates.append((new_gamestate, num_gamestate))

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
    """Encodes the pieces as a 1 dimensional array

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
                # (
                #     "110000000000000"
                #     "000000101101101"
                #     "101101000000000"
                #     "000000000101101"
                #     "101101101000000"
                #     "000000000000101"
                #     "101101101101000"
                #     "000000000000000"
                #     "101101101101000"
                #     "000000000000000"
                # )
            )
        else:
            self._pieces = pieces

    def get_board_index(self, pos):
        return (10 * pos[1] + pos[0]) // 2 * 3

    def get_pieces(self, player_id):
        pieces = []
        for y in range(10):
            for x in range(5):
                board_index = 15 * y + 3 * x
                if self._pieces[board_index] and self._pieces[board_index + 2] == player_id:
                    square_offset = (board_index // 3 + 1) % 10
                    pieces.append(Piece((2 * x + (1 <= square_offset <= 5), y), self._pieces[board_index + 1]))

        return pieces

    def remove_piece(self, pos):
        board_index = self.get_board_index(pos)

        if not self._pieces[board_index]:
            return False

        self._pieces[board_index:board_index + 3] = bitarray.bitarray('000')

        return True

    def move_piece(self, startpos, endpos):
        startpos_board_index = self.get_board_index(startpos)

        if not self._pieces[startpos_board_index]:
            return False

        endpos_board_index = self.get_board_index(endpos)

        if self._pieces[endpos_board_index]:
            return False

        self._pieces[endpos_board_index] = True
        self._pieces[endpos_board_index + 1] = self._pieces[startpos_board_index + 1]
        self._pieces[endpos_board_index + 2] = self._pieces[startpos_board_index + 2]

        self._pieces[startpos_board_index:startpos_board_index + 3] = bitarray.bitarray('000')

        return True

    def crown_piece(self, pos):
        board_index = self.get_board_index(pos)

        if not self._pieces[board_index]:
            return False

        self._pieces[board_index + 1] = True

        return True

    def get_player_from_piece(self, pos):
        board_index = self.get_board_index(pos)

        if self._pieces[board_index]:
            return self._pieces[board_index + 1]

        return -1


NO_TIE_REQUEST = 2
INVALID_TIE_REQUEST = 3


class GameState:
    def __init__(self, board=None, turn=1, player=0, tie_request=NO_TIE_REQUEST):
        if not board:
            self.board = BoardGrid()
        else:
            self.board = deepcopy(board)

        self.tie_request = tie_request
        self.turn = turn
        self.current_player = player

    def is_opponent_winning(self):
        return not DraughtsRules.get_all_possible_moves(self, self.current_player)

    def is_draw(self, history):
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
            tie_request=self.tie_request if self.tie_request == self.current_player else NO_TIE_REQUEST
        )

        captured_pieces = DraughtsRules.get_captured_pieces(
            piece,
            move,
            self.board.get_pieces(not self.current_player)
        )

        for captured_piece in captured_pieces:
            newstate.board.remove_piece(captured_piece.pos)

        newstate.board.move_piece(piece.pos, move[-1])

        if move[-1][1] == (0, 9)[newstate.board.get_player_from_piece(move[-1])]:
            newstate.board.crown_piece(move[-1])

        return newstate


class History:
    def __init__(self):
        self.movelist = []
        self.gamestates = []
        self.onevs2_moves = 0  # draw if 10
        self.onevs3_moves = 0  # draw if 32
        self.consecutive_moves_with_kings = 0  # draw if 50

    def get_moves_in_pairs(self):
        index = 0
        while index < len(self.movelist):
            if index + 1 < len(self.movelist):
                yield (self.movelist[index], self.movelist[index + 1])
                index += 1
            else:
                yield (self.movelist[index],)

            index += 1

    def convert_pos_to_index(self, pos):
        return (10 * pos[1] + pos[0]) // 2 + 1

    def convert_move_to_str(self, move):
        return '{0}{1}{2}'.format(
            self.convert_pos_to_index(move[0]),
            'x' if move[2] else '-',
            self.convert_pos_to_index(move[1][-1])
        )

    def movelist_as_string(self):
        str_movelist = [' '.join(self.convert_move_to_str(move) for move in moves)
                        for moves in self.get_moves_in_pairs()]

        return str_movelist

    def add_gamestate(self, gamestate):
        num_gamestate = 1
        for state in self.gamestates:
            if gamestate.current_player == state[0].current_player and gamestate.pieces == state[0].pieces:
                num_gamestate += 1

        self.gamestates.append((gamestate, num_gamestate))

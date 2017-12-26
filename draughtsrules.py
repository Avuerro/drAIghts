directions = (
    (-1, -1),  # top left
    (1, -1),  # top right
    (-1, 1),  # bottom right
    (1, 1)  # bottom left
)


class DraughtsRules:
    @staticmethod
    def get_moves(
            moves,
            piece_is_king,
            player_piece_positions,
            opponent_piece_positions,
            captured_piece_positions,
            forward_directions
    ):
        if not piece_is_king:
            newpositions = []
            capturedpositions = []
            for direction in directions:
                (x, y) = moves[-1]
                newpos = (x + direction[0], y + direction[1])
                if 0 <= newpos[0] <= 9 and 0 <= newpos[1] <= 9:
                    if newpos in opponent_piece_positions:
                        after_capturepos = (newpos[0] + direction[0], newpos[1] + direction[1])
                        if after_capturepos not in player_piece_positions and after_capturepos not in \
                                opponent_piece_positions and 0 <= after_capturepos[0] <= 9 and 0 <= \
                                after_capturepos[1] <= 9:
                            capturedpositions.append([newpos])
                            capturedpositions[-1].append(after_capturepos)
                    elif not captured_piece_positions and direction in forward_directions and newpos not \
                            in player_piece_positions:
                        newpositions.append(newpos)

            if capturedpositions:
                for capturedpos in capturedpositions:
                    if capturedpos not in captured_piece_positions:
                        moves.append([capturedpos[1]])

                        opponent_positions = [pos for pos in opponent_piece_positions if
                                              pos != capturedpos[0]]
                        captured_piece_positions.append(capturedpos[0])

                        newmoves = moves[-1]

                        newmoves = DraughtsRules.get_moves(newmoves, piece_is_king, player_piece_positions,
                                                           opponent_positions, captured_piece_positions,
                                                           forward_directions)

                        newmoves = newmoves[1:]
                        if newmoves:
                            moves[-1].append(newmoves)
            else:
                for newpos in newpositions:
                    moves.append([newpos])

            return moves[1:]
        else:
            newpositions = []
            capturedpositions = []
            for direction in directions:
                (x, y) = moves[-1]
                newpos = (x + direction[0], y + direction[1])
                while 0 <= newpos[0] <= 9 and 0 <= newpos[1] <= 9:
                    if newpos in captured_piece_positions:
                        break
                    if newpos in player_piece_positions:
                        newpos = (newpos[0] - direction[0], newpos[1] - direction[1])
                        while newpos != moves[-1]:
                            if not captured_piece_positions:
                                newpositions.append(newpos)
                            newpos = (newpos[0] - direction[0], newpos[1] - direction[1])

                        break
                    elif newpos in opponent_piece_positions:
                        if (newpos[0] + direction[0], newpos[1] + direction[1]) not in player_piece_positions and (
                                newpos[0] + direction[0],
                                newpos[1] + direction[1]) not in opponent_piece_positions and 0 <= newpos[0] + \
                                direction[0] <= 9 and 0 <= newpos[1] + direction[1] <= 9:
                            capturedpositions.append([newpos, []])
                            newpos = (newpos[0] + direction[0], newpos[1] + direction[1])
                            while newpos not in player_piece_positions and newpos not in opponent_piece_positions \
                                    and 0 <= newpos[0] <= 9 and 0 <= newpos[1] <= 9:
                                capturedpositions[-1][1].append(newpos)
                                newpos = (newpos[0] + direction[0], newpos[1] + direction[1])

                        break
                    elif not captured_piece_positions:
                        newpositions.append(newpos)

                    newpos = (newpos[0] + direction[0], newpos[1] + direction[1])

            if capturedpositions:
                for capturedpos in capturedpositions:
                    opponent_positions = [pos for pos in opponent_piece_positions if pos != capturedpos[0]]
                    captured_positions = captured_piece_positions + [capturedpos[0]]

                    for move in capturedpos[1]:
                        if move not in captured_piece_positions:
                            moves.append([move])
                            newmoves = [move]
                            newmoves = DraughtsRules.get_moves(newmoves, piece_is_king, player_piece_positions,
                                                               opponent_positions, captured_positions,
                                                               forward_directions)
                            newmoves = newmoves[1:]
                            if newmoves:
                                moves[-1].append(newmoves)

                if captured_piece_positions:
                    return moves
                else:
                    return [moves[1:]]
            else:
                for newpos in newpositions:
                    moves.append([newpos])

                return moves[1:]

    @staticmethod
    def flatten_movelist(moves):
        if isinstance(moves, list):
            if len(moves) == 2 and not isinstance(moves[0], list) and isinstance(moves[1], list):
                flattenedlist = [moves[0]]
                flattenedlist.extend(DraughtsRules.flatten_movelist(moves[1]))
                return flattenedlist
            else:
                flattenedlist = []
                for move in moves:
                    flattenedlist.append(DraughtsRules.flatten_movelist(move))
                return flattenedlist

        return moves

    @staticmethod
    def get_longest_moves(action_list, moves):
        action_list = list(action_list)
        possible_moves = []
        branched = False
        for index in range(len(moves)):
            if isinstance(moves[index], list):
                branched = True
                possible_moves.extend(DraughtsRules.get_longest_moves(action_list, moves[index]))
            else:
                action_list.append(moves[index])

        if not branched:
            possible_moves.append(action_list)

        possible_moves.sort(key=lambda move: len(move), reverse=True)
        max_length = len(possible_moves[0])
        possible_moves = [move for move in possible_moves if len(move) == max_length]

        return possible_moves

    @staticmethod
    def get_piece_possible_moves(piece, player_pieces, opponent_pieces, player_id):
        player_piece_positions = [p.pos for p in player_pieces]
        opponent_piece_positions = [p.pos for p in opponent_pieces]
        forward_directions = directions[2 * player_id:2 * player_id + 2]

        moves = DraughtsRules.get_longest_moves(
            [],
            DraughtsRules.flatten_movelist(
                DraughtsRules.get_moves(
                    [piece.pos],
                    piece.is_king,
                    player_piece_positions,
                    opponent_piece_positions,
                    [],
                    forward_directions
                )
            )
        )

        possible_moves = list(set(tuple(move) for move in moves))

        return possible_moves

    @staticmethod
    def get_orientation(startpos, endpos):
        dx = 1 if startpos[0] < endpos[0] else -1
        dy = 1 if startpos[1] < endpos[1] else -1

        return dx, dy

    @staticmethod
    def get_captured_pieces(piece, move, opponent_pieces):
        pos = piece.pos
        captured_pieces = []
        opponent_pieces = opponent_pieces[:]
        for movepos in move:
            direction = DraughtsRules.get_orientation(pos, movepos)

            while pos != movepos:
                for opponent_piece in opponent_pieces:
                    if pos == opponent_piece.pos:
                        captured_pieces.append(opponent_piece)
                        opponent_pieces.remove(opponent_piece)
                        break

                pos = (pos[0] + direction[0], pos[1] + direction[1])

        return captured_pieces

    @staticmethod
    def get_all_possible_moves(currentstate, player_id):
        player_pieces = currentstate.board.get_pieces(player_id)
        opponent_pieces = currentstate.board.get_pieces(not player_id)

        all_moves = []
        max_captures = 0
        for piece in player_pieces:
            piece_moves = DraughtsRules.get_piece_possible_moves(piece, player_pieces, opponent_pieces, player_id)
            if piece_moves and piece_moves[0]:
                num_captures = len(DraughtsRules.get_captured_pieces(piece, piece_moves[0], opponent_pieces))
                if num_captures > max_captures:
                    all_moves = [(piece, piece_moves)]
                    max_captures = num_captures
                elif num_captures == max_captures:
                    all_moves.append((piece, piece_moves))

        return all_moves

    @staticmethod
    def is_valid_move(piece, move, currentstate, player_id):
        player_pieces = currentstate.board.get_pieces(player_id)

        if piece in player_pieces:
            possible_moves = DraughtsRules.get_piece_possible_moves(
                piece,
                player_pieces,
                currentstate.board.get_pieces(not player_id),
                player_id
            )

            return move in possible_moves

        return False

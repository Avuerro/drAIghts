import pygame
from draughtsrules import DraughtsRules

class EventManager:
    def __init__(self, game):
        self._game = game

    def scroll(self, direction):
        self._game.notify(('scroll', direction))

    def send_tie_request(self):
        self._game.notify(('tie',))

    def redraw_sidepanel(self):
        self._game.notify(('redraw_sidepanel',))

    def redraw_board(self):
        self._game.notify(('redraw_board',))

    def highlight_spaces(self, spaces):
        self._game.notify(('highlight_spaces', spaces))

    def highlight_button(self, button_rect):
        self._game.notify(('highlight_button', button_rect))


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


class HumanPlayer(Player):
    def __init__(self, player_id, manager, button_rects, switch_sides, board_size, square_size):
        super(HumanPlayer, self).__init__(player_id)

        self.manager = manager

        self.button_rects = button_rects
        self.switch_sides = switch_sides
        self.board_size = board_size
        self.square_size = square_size

        self.mousebutton_pressed = False
        self.button_selected = False

        self.highlighted_moves = None
        self.player_pieces = []
        self.all_possible_moves = None

    def get_board_pos(self, mouse_pos, player_id, switch_sides):
        if (self.board_size[0] - 10 * self.square_size) <= mouse_pos[0] <= self.board_size[0] and 0 <= \
                mouse_pos[1] <= self.board_size[1]:
            for y in range(10):
                for x in range(10):
                    min_x = (self.board_size[0] - (10 - x) * self.square_size)
                    max_x = (self.board_size[0] - (9 - x) * self.square_size)
                    min_y = (y * self.square_size)
                    max_y = ((y + 1) * self.square_size)
                    if min_x <= mouse_pos[0] <= max_x and min_y <= mouse_pos[1] <= max_y:
                        if player_id and switch_sides:
                            return 9 - x, 9 - y
                        else:
                            return x, y

        return None

    def get_action(self, currentstate, history):
        self.mousebutton_pressed = False
        self.button_selected = False
        self.highlighted_moves = None

        self.player_pieces = currentstate.board.get_pieces(self.player_id)
        self.all_possible_moves = DraughtsRules.get_all_possible_moves(currentstate, self.player_id)

        while True:
            mousepos = pygame.mouse.get_pos()

            if self.mousebutton_pressed and not any(pygame.mouse.get_pressed()):
                self.mousebutton_pressed = False
            if not self.mousebutton_pressed and any(pygame.mouse.get_pressed()):
                self.button_selected = False
                self.mousebutton_pressed = True
                for rect_index in range(len(self.button_rects)):
                    rect = self.button_rects[rect_index]
                    if rect[0] < mousepos[0] < rect[2] and rect[1] < mousepos[1] < rect[3]:
                        if rect_index == 0:
                            self.manager.scroll(-1)
                        elif rect_index == 1:
                            self.manager.scroll(1)
                        elif rect_index == 2:
                            if currentstate.tie_request == (not self.player_id):
                                return ACTION_TIE
                            else:
                                self.manager.send_tie_request()
                        elif rect_index == 3:
                            return ACTION_RESIGN
            elif self.button_selected and not any(
                    rect[0] < mousepos[0] < rect[2] and rect[1] < mousepos[1] < rect[3] for rect in self.button_rects):
                self.button_selected = False
                self.manager.redraw_sidepanel()
            else:
                for rect in self.button_rects:
                    if rect[0] < mousepos[0] < rect[2] and rect[1] < mousepos[1] < rect[3] and not self.button_selected:
                        self.manager.highlight_button(rect)
                        self.button_selected = True
                        break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return ACTION_RESIGN
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = self.get_board_pos(event.pos, self.player_id, self.switch_sides)

                    if pos:
                        if not self.highlighted_moves:
                            if any(pos == piece.pos for piece in self.player_pieces):
                                piece = next(piece for piece in self.player_pieces if pos == piece.pos)
                                if any(piece == moves[0] for moves in self.all_possible_moves):
                                    self.highlighted_moves = self.all_possible_moves[next(
                                        index for index in range(len(self.all_possible_moves)) if
                                        self.all_possible_moves[index][0] == piece)]

                                    spaces_to_highlight = [set(), set()]
                                    for spaces in self.highlighted_moves[1]:
                                        spaces_to_highlight[0].update(spaces[:-1])
                                        spaces_to_highlight[1].add(spaces[-1])

                                    spaces_to_highlight[0] = list(spaces_to_highlight[0])
                                    spaces_to_highlight[1] = list(spaces_to_highlight[1])

                                    self.manager.highlight_spaces(spaces_to_highlight)
                        else:
                            for move in self.highlighted_moves[1]:
                                if pos == move[-1]:
                                    return self.highlighted_moves[0], move

                            if not any(pos == piece.pos for piece in self.player_pieces):
                                self.highlighted_moves = None
                                self.manager.redraw_board()

    def end_turn(self, current_state):
        self.highlighted_moves = None

    def end_game(self, history, winner):
        # todo: save pdn file of match
        if winner == self.player_id:
            print('winner: {0}'.format(int(winner)))
        else:
            print('loser: {0}'.format(int(not winner)))

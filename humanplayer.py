import pygame

from draughtsrules import DraughtsRules
import player
from draights import TIE_REQUEST_TURN


class EventManager:
    def __init__(self, game):
        self._game = game

    def scroll(self, direction):
        self._game.notify(('scroll', direction))

    def redraw_sidepanel(self):
        self._game.notify(('redraw_sidepanel',))

    def redraw_board(self):
        self._game.notify(('redraw_board',))

    def highlight_spaces(self, spaces):
        self._game.notify(('highlight_spaces', spaces))

    def highlight_button(self, button_rect):
        self._game.notify(('highlight_button', button_rect))


class HumanPlayer(player.Player):
    def __init__(self, player_id, manager, button_rects, switch_sides, board_size, square_size):
        super(HumanPlayer, self).__init__(player_id)

        self.manager = manager

        self.button_rects = button_rects
        self.switch_sides = switch_sides
        self.board_size = board_size
        self.square_size = square_size

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
        mousebutton_pressed = False
        button_selected = False

        player_pieces = currentstate.board.get_pieces(self.player_id)
        all_possible_moves = DraughtsRules.get_all_possible_moves(currentstate, self.player_id)
        highlighted_moves = None
        tie_request = False

        while True:
            mousepos = pygame.mouse.get_pos()

            if mousebutton_pressed and not any(pygame.mouse.get_pressed()):
                mousebutton_pressed = False
            if not mousebutton_pressed and any(pygame.mouse.get_pressed()):
                button_selected = False
                mousebutton_pressed = True
                for rect_index in range(len(self.button_rects)):
                    rect = self.button_rects[rect_index]
                    if rect[0] < mousepos[0] < rect[2] and rect[1] < mousepos[1] < rect[3]:
                        if rect_index == 0:
                            self.manager.scroll(-1)
                        elif rect_index == 1:
                            self.manager.scroll(1)
                        elif rect_index == 2:
                            if currentstate.tie_request == (not self.player_id):
                                return player.ACTION_TIE
                            elif currentstate.turn >= TIE_REQUEST_TURN:
                                tie_request = True
                        elif rect_index == 3:
                            return player.ACTION_RESIGN
            elif button_selected and not any(
                    rect[0] < mousepos[0] < rect[2] and rect[1] < mousepos[1] < rect[3] for rect in self.button_rects):
                button_selected = False
                self.manager.redraw_sidepanel()
            else:
                for rect in self.button_rects:
                    if rect[0] < mousepos[0] < rect[2] and rect[1] < mousepos[1] < rect[3] and not button_selected:
                        self.manager.highlight_button(rect)
                        button_selected = True
                        break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return player.ACTION_RESIGN
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = self.get_board_pos(event.pos, self.player_id, self.switch_sides)

                    if pos:
                        if not highlighted_moves:
                            if any(pos == piece.pos for piece in player_pieces):
                                piece = next(piece for piece in player_pieces if pos == piece.pos)
                                if any(piece == moves[0] for moves in all_possible_moves):
                                    highlighted_moves = all_possible_moves[next(
                                        index for index in range(len(all_possible_moves)) if
                                        all_possible_moves[index][0] == piece)]

                                    spaces_to_highlight = [set(), set()]
                                    for spaces in highlighted_moves[1]:
                                        spaces_to_highlight[0].update(spaces[:-1])
                                        spaces_to_highlight[1].add(spaces[-1])

                                    spaces_to_highlight[0] = list(spaces_to_highlight[0])
                                    spaces_to_highlight[1] = list(spaces_to_highlight[1])

                                    self.manager.highlight_spaces(spaces_to_highlight)
                        else:
                            for move in highlighted_moves[1]:
                                if pos == move[-1]:
                                    return highlighted_moves[0], move, tie_request

                            if not any(pos == piece.pos for piece in player_pieces):
                                highlighted_moves = None
                                self.manager.redraw_board()

import configparser
import math
from ast import literal_eval
from copy import deepcopy

import pygame

import board
import graphics
import player
from draughtsrules import DraughtsRules


class ItemParser:
    def parse_value(self, value):
        try:
            return literal_eval(value)
        except SyntaxError or ValueError:
            return value

    def read(self, item_list):
        items = {}

        for item in item_list:
            (key, value) = item
            items[key] = self.parse_value(value.replace(' ', ''))

        return items


class Display:
    TIME_PER_MOVE = 30
    BOARD_SIZE = (576, 480)
    PANEL_SIZE = (288, 480)

    def __init__(self, colors):
        pygame.init()
        self.window = pygame.display.set_mode(
            (Display.BOARD_SIZE[0] + Display.PANEL_SIZE[0], max(Display.BOARD_SIZE[1], Display.PANEL_SIZE[1])))
        pygame.display.set_caption('DrAIghts')

        self.board_graphics = graphics.BoardGraphics(Display.BOARD_SIZE, colors)
        self.panel_graphics = graphics.PanelGraphics(Display.PANEL_SIZE, colors)

        self.background = pygame.Surface(self.window.get_size(), pygame.SRCALPHA, 32)

    def draw_board_background(self):
        surface = self.board_graphics.get_board_background_surface()
        self.background.blit(surface, [0, 0, surface.get_width(), surface.get_height()])
        pygame.display.update()

    def draw_pieces(self, player_pieces, opponent_pieces, current_player, switch_sides, captured_piece_nums,
                    movingpiece=None):
        surface = self.board_graphics.get_piece_surface(player_pieces, opponent_pieces, current_player, switch_sides)

        if movingpiece:
            if switch_sides:
                pos = (9 - movingpiece.pos[0], 9 - movingpiece.pos[1]) if current_player else movingpiece.pos
            else:
                pos = movingpiece.pos
            self.board_graphics.draw_current_player_piece(surface, pos, movingpiece.is_king, current_player)

        self.background.blit(surface, (0, 0))

        surface = self.board_graphics.get_captured_piece_surface(captured_piece_nums)
        self.background.blit(surface, (0, 0))

    def draw_highlighted_spaces(self, spaces_list, switch_sides):
        if switch_sides:
            for spaces in spaces_list:
                for index in range(len(spaces)):
                    spaces[index] = (9 - spaces[index][0], 9 - spaces[index][1])

        surface = self.board_graphics.get_highlight_surface(spaces_list)
        self.background.blit(surface, (0, 0))

    def draw_sidepanel_background(self):
        surface = self.panel_graphics.get_panel_background_surface()
        self.background.blit(surface, [Display.BOARD_SIZE[0], 0, surface.get_width(), surface.get_height()])

    def draw_history(self, movelist, scrollindex):
        surface = self.panel_graphics.get_movelist_surface(movelist, scrollindex)
        self.background.blit(surface, [Display.BOARD_SIZE[0], 0, surface.get_width(), surface.get_height()])

    def draw_console_messages(self, current_player, tie_request):
        surface = self.panel_graphics.get_consolemessage_surface(current_player, tie_request)
        self.background.blit(surface, [Display.BOARD_SIZE[0], 0, surface.get_width(), surface.get_height()])

    def draw_button_overlay(self, button_rect):
        surface = self.panel_graphics.get_highlight_button_surface(button_rect)
        self.background.blit(surface, [button_rect[0], button_rect[1], surface.get_width(), surface.get_height()])

    def render_to_screen(self):
        self.window.blit(self.background, (0, 0))
        pygame.display.update()


class Game:
    MOVE_TIME = 15

    def __init__(self, gamesettings):
        self.display = Display(gamesettings['colors'])

        self.display_screen = gamesettings['game']['display_screen']
        self.switch_sides = gamesettings['game']['switch_sides']

        self.current_state = board.GameState()
        self.history = board.History()

        self.players = [None, None]
        eventmanager = player.EventManager(self)

        board_size = Display.BOARD_SIZE
        square_size = min(board_size) / 10
        panel_size = Display.PANEL_SIZE
        buttonsize_with_border = (panel_size[0], panel_size[1] / 10)
        button_center_offset = max(buttonsize_with_border) / 40
        buttonsize = (buttonsize_with_border[0] - 2 * button_center_offset,
                      buttonsize_with_border[1] - 2 * button_center_offset)
        button_rects = []
        button_rects.append(
            (
                board_size[0] + buttonsize[0] - 3 * button_center_offset,
                button_center_offset,
                board_size[0] + buttonsize[0] + button_center_offset,
                4 * button_center_offset + 1
            )
        )
        button_rects.append(
            (
                board_size[0] + buttonsize[0] - 3 * button_center_offset,
                7 * buttonsize_with_border[1] - 4 * button_center_offset,
                board_size[0] + buttonsize[0] + button_center_offset,
                7 * buttonsize_with_border[1] - button_center_offset
            )
        )
        button_rects.append(
            (
                board_size[0] + button_center_offset,
                8 * buttonsize_with_border[1] + button_center_offset,
                board_size[0] + button_center_offset + buttonsize[0],
                8 * buttonsize_with_border[1] + buttonsize[1] + button_center_offset
            )
        )
        button_rects.append(
            (
                board_size[0] + button_center_offset,
                9 * buttonsize_with_border[1] + button_center_offset,
                board_size[0] + button_center_offset + buttonsize[0],
                9 * buttonsize_with_border[1] + buttonsize[1] + button_center_offset
            )
        )
        for i in range(2):
            # todo: add if for non-human players
            self.players[i] = player.HumanPlayer(i, eventmanager, button_rects, self.switch_sides,
                                                 board_size, square_size)

        self.scrollindex = 0
        self.captured_piece_nums = (0, 0)

        self.keepgoing = True

    def render_all(self):
        self.display.draw_board_background()
        self.display.draw_pieces(
            self.current_state.board.get_pieces(self.current_state.current_player),
            self.current_state.board.get_pieces(not self.current_state.current_player),
            self.current_state.current_player,
            self.switch_sides,
            self.captured_piece_nums
        )

        self.display.draw_sidepanel_background()
        self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
        self.display.draw_console_messages(self.current_state.current_player, self.current_state.tie_request)
        self.display.render_to_screen()

    def show_move_anim(self, piece, move, captured_pieces):
        player_pieces = self.current_state.board.get_pieces(self.current_state.current_player)
        player_pieces.remove(piece)
        opponent_pieces = self.current_state.board.get_pieces(not self.current_state.current_player)

        clock = pygame.time.Clock()
        for index in range(len(move)):
            x, y = piece.pos
            dx = move[index][0] - x
            dy = move[index][1] - y

            for i in range(Game.MOVE_TIME):
                pygame.event.clear()
                piece.pos = (
                    x + dx * math.sin(float(i) / float(Game.MOVE_TIME) * math.pi / 2),
                    y + dy * math.sin(float(i) / float(Game.MOVE_TIME) * math.pi / 2)
                )

                self.display.draw_board_background()
                self.display.draw_pieces(
                    player_pieces,
                    opponent_pieces,
                    self.current_state.current_player,
                    self.switch_sides,
                    self.captured_piece_nums,
                    movingpiece=piece
                )
                self.display.render_to_screen()
                clock.tick(60)

            if captured_pieces:
                opponent_pieces.remove(captured_pieces[0])
                del captured_pieces[0]

    def run(self):
        self.keepgoing = True

        for p in self.players:
            p.initialize()

        while self.keepgoing:
            if self.display_screen:
                self.render_all()

            action = self.players[self.current_state.current_player].get_action(
                deepcopy(self.current_state),
                deepcopy(self.history)
            )

            if self.current_state.tie_request == board.INVALID_TIE_REQUEST:
                self.current_state.tie_request = board.NO_TIE_REQUEST

            if isinstance(action, int):
                # todo: handle player wins / ties
                if action == player.ACTION_RESIGN:
                    print("{0} wins".format('Black' if not self.current_state.current_player else 'White'))
                if action == player.ACTION_TIE:
                    if self.current_state.turn >= 40:
                        print(0.5)
                    else:
                        raise Exception("Tie requested on turn {0}".format(self.current_state.turn))
                break

            piece = action[0]
            move = action[1]
            if not DraughtsRules.is_valid_move(piece, move, self.current_state, self.current_state.current_player):
                raise Exception('Invalid move')

            captured_pieces = DraughtsRules.get_captured_pieces(
                piece,
                move,
                self.current_state.board.get_pieces(not self.current_state.current_player)
            )

            self.history.movelist.append((piece.pos, action[1], len(captured_pieces) > 0))
            self.captured_piece_nums = (
                self.captured_piece_nums[0] + (self.current_state.current_player == 1) * len(captured_pieces),
                self.captured_piece_nums[1] + (self.current_state.current_player == 0) * len(captured_pieces))

            if self.display_screen:
                self.show_move_anim(deepcopy(piece), move, captured_pieces)

            self.current_state = self.current_state.get_successor(piece, move)

            if self.current_state.is_opponent_winning():
                # todo: end game and announce winner
                print("{0} wins".format('Black' if not self.current_state.current_player else 'White'))
                break

            #     # todo: check if gamestate is a draw
            #     # game is a draw if:
            #     #   - both players have played 5 turns if piece count == 1 king vs 1 king + any piece
            #     #   - both players have played 16 turns if piece count == 1 king vs 1 king + 2 pieces
            #     #   - both players have played 25 consecutive turns with just kings without capturing anything
            #     #   - the same configuration has appeared for the third time on the turn of the same player

            # switch players and set history panel to last move
            if self.current_state.current_player:
                self.scrollindex = max(0, self.current_state.turn - 12)
            else:
                self.scrollindex = max(0, self.current_state.turn - 12)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.keepgoing = False

    def notify(self, event):
        if event[0] == 'scroll':
            self.scrollindex = max(0, min(self.current_state.turn - 13, self.scrollindex + event[1]))
            if self.display_screen:
                self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                self.display.render_to_screen()
        elif event[0] == 'tie':
            if self.current_state.turn >= 40:
                self.current_state.tie_request = self.current_state.current_player
            else:
                self.current_state.tie_request = board.INVALID_TIE_REQUEST

            self.display.draw_sidepanel_background()
            self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
            self.display.draw_console_messages(self.current_state.current_player, self.current_state.tie_request)
            self.display.render_to_screen()
        elif event[0] == 'redraw_sidepanel':
            if self.display_screen:
                self.display.draw_sidepanel_background()
                self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                self.display.draw_console_messages(self.current_state.current_player, self.current_state.tie_request)
                self.display.render_to_screen()
        elif event[0] == 'redraw_board':
            if self.display_screen:
                self.display.draw_board_background()
                self.display.draw_pieces(
                    self.current_state.board.get_pieces(self.current_state.current_player),
                    self.current_state.board.get_pieces(not self.current_state.current_player),
                    self.current_state.current_player,
                    self.switch_sides,
                    self.captured_piece_nums
                )
                self.display.render_to_screen()
        elif event[0] == 'highlight_spaces':
            if self.display_screen:
                self.display.draw_highlighted_spaces(event[1],
                                                     True if (self.switch_sides and
                                                              self.current_state.current_player) else False)
                self.display.render_to_screen()
        elif event[0] == 'highlight_button':
            if self.display_screen:
                self.display.draw_sidepanel_background()
                self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                self.display.draw_console_messages(self.current_state.current_player, self.current_state.tie_request)
                self.display.draw_button_overlay(event[1])
                self.display.render_to_screen()


def main():
    # todo: add command line OptionParser
    config = configparser.ConfigParser()
    config.read(['draights.cfg'])
    settings = {}
    for section in config.sections():
        settings[section] = ItemParser().read(config.items(section))

    game = Game(settings)
    game.run()

    # todo: add ability to disable graphics


if __name__ == "__main__":
    main()

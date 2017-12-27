import argparse
import configparser
import copy
import math
import os
from ast import literal_eval

import pygame

import board
import graphics
import humanplayer
import player
from draughtsrules import DraughtsRules


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

    def announce_winner(self, is_winner, winner_name="", winner_id=0):
        surface = self.panel_graphics.get_continuebutton_surface()
        self.background.blit(surface, [Display.BOARD_SIZE[0], 0, surface.get_width(), surface.get_height()])

        if is_winner:
            win_surface = self.panel_graphics.get_win_message_surface(winner_name, winner_id)
            self.background.blit(win_surface,
                                 [Display.BOARD_SIZE[0], 0, win_surface.get_width(), win_surface.get_height()])
        else:
            tie_surface = self.panel_graphics.get_tie_message_surface()
            self.background.blit(tie_surface,
                                 [Display.BOARD_SIZE[0], 0, tie_surface.get_width(), tie_surface.get_height()])

    def render_to_screen(self):
        self.window.blit(self.background, (0, 0))
        pygame.display.update()


TIE_REQUEST_TURN = 40


class Game:
    MOVE_TIME = 15

    def __init__(self,
                 players=None,
                 disp_graphics=True,
                 switch_sides=False,
                 ):

        self.display_screen = disp_graphics
        self.switch_sides = switch_sides

        if self.display_screen:
            self.display = Display(colors)

        self.current_state = board.GameState()
        self.history = board.History(self.current_state)

        self.players = [None, None]
        self.winner = -1
        eventmanager = humanplayer.EventManager(self)

        board_size = Display.BOARD_SIZE
        square_size = min(board_size) / 10
        panel_size = Display.PANEL_SIZE
        buttonsize_with_border = (panel_size[0], panel_size[1] / 10)
        button_center_offset = max(buttonsize_with_border) / 40
        buttonsize = (buttonsize_with_border[0] - 2 * button_center_offset,
                      buttonsize_with_border[1] - 2 * button_center_offset)
        button_rects = [
            (
                board_size[0] + buttonsize[0] - 3 * button_center_offset,
                button_center_offset,
                board_size[0] + buttonsize[0] + button_center_offset,
                4 * button_center_offset + 1
            ),
            (
                board_size[0] + buttonsize[0] - 3 * button_center_offset,
                7 * buttonsize_with_border[1] - 4 * button_center_offset,
                board_size[0] + buttonsize[0] + button_center_offset,
                7 * buttonsize_with_border[1] - button_center_offset
            ),
            (
                board_size[0] + button_center_offset,
                8 * buttonsize_with_border[1] + button_center_offset,
                board_size[0] + button_center_offset + buttonsize[0],
                8 * buttonsize_with_border[1] + buttonsize[1] + button_center_offset
            ),
            (
                board_size[0] + button_center_offset,
                9 * buttonsize_with_border[1] + button_center_offset,
                board_size[0] + button_center_offset + buttonsize[0],
                9 * buttonsize_with_border[1] + buttonsize[1] + button_center_offset
            )
        ]

        self.button_rects = [
            button_rects[0],
            button_rects[1],
            (
                board_size[0] + button_center_offset,
                8 * buttonsize_with_border[1] + button_center_offset,
                board_size[0] + button_center_offset + buttonsize[0],
                8 * buttonsize_with_border[1] + button_center_offset + 2 * (
                        buttonsize_with_border[1] - button_center_offset)
            )
        ]

        for i in range(2):
            if players[i][1].__name__ == 'HumanPlayer':
                self.players[i] = players[i][1](i, eventmanager, button_rects, self.switch_sides,
                                                board_size, square_size, name=players[i][0])
            else:
                self.players[i] = players[i][1](i, name=players[i][0])

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
        capt_piece_index = 0

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
                opponent_pieces.remove(captured_pieces[capt_piece_index])
                capt_piece_index += 1

    def run(self):
        self.keepgoing = True

        for p in self.players:
            p.initialize()

        while self.keepgoing:
            if self.display_screen:
                self.render_all()

            action = self.players[self.current_state.current_player].get_action(
                copy.deepcopy(self.current_state),
                copy.deepcopy(self.history)
            )

            if self.current_state.tie_request == board.INVALID_TIE_REQUEST:
                self.current_state.tie_request = board.NO_TIE_REQUEST

            if isinstance(action, int):
                if action == player.ACTION_RESIGN:
                    self.winner = not self.current_state.current_player
                    break
                if action == player.ACTION_TIE:
                    if self.current_state.turn >= TIE_REQUEST_TURN and self.current_state.tie_request == \
                            (not self.current_state.current_player):
                        self.winner = -1
                        break
                    else:
                        raise Exception("Tie requested on turn {0}".format(self.current_state.turn))

            piece, move, tie_request = action
            if not DraughtsRules.is_valid_move(piece, move, self.current_state, self.current_state.current_player):
                raise Exception('Invalid move')

            if tie_request:
                if self.current_state.turn < TIE_REQUEST_TURN:
                    raise Exception("Tie requested on turn {0}".format(self.current_state.turn))

                self.current_state.tie_request = self.current_state.current_player

            captured_pieces = DraughtsRules.get_captured_pieces(
                piece,
                move,
                self.current_state.board.get_pieces(not self.current_state.current_player)
            )

            self.captured_piece_nums = (
                self.captured_piece_nums[0] + (self.current_state.current_player == 1) * len(captured_pieces),
                self.captured_piece_nums[1] + (self.current_state.current_player == 0) * len(captured_pieces))

            if self.display_screen:
                self.show_move_anim(copy.deepcopy(piece), move, captured_pieces)

            old_gamestate = copy.copy(self.current_state)
            self.current_state = self.current_state.get_successor(piece, move)
            self.history.add_move(self.current_state, (piece.pos, move, len(captured_pieces) > 0), old_gamestate)

            if self.current_state.is_opponent_winning():
                self.winner = not self.current_state.current_player
                break
            elif self.current_state.is_draw(self.history):
                self.winner = -1
                break

            # switch players and set history panel to last move
            if self.current_state.current_player:
                self.scrollindex = max(0, self.current_state.turn - 12)
            else:
                self.scrollindex = max(0, self.current_state.turn - 12)

            if self.display_screen:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.keepgoing = False

        for p in self.players:
            p.end_game(self.history, self.winner)

        if self.display_screen:
            self.display.draw_sidepanel_background()
            self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
            self.display.announce_winner(self.winner >= 0, self.players[self.winner].name, self.winner)
            self.display.render_to_screen()

            keepgoing = True
            button_selected = False
            mousebutton_pressed = False
            while keepgoing:
                mousepos = pygame.mouse.get_pos()

                selectedbutton = -1
                for index in range(len(self.button_rects)):
                    if self.button_rects[index][0] < mousepos[0] < self.button_rects[index][2] and \
                            self.button_rects[index][1] < mousepos[1] < self.button_rects[index][3]:
                        selectedbutton = index
                        break

                if not any(pygame.mouse.get_pressed()):
                    mousebutton_pressed = False

                if selectedbutton >= 0:
                    if not button_selected:
                        self.display.draw_sidepanel_background()
                        self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                        self.display.announce_winner(self.winner >= 0, self.players[self.winner].name, self.winner)
                        self.display.draw_button_overlay(self.button_rects[index])
                        self.display.render_to_screen()

                        button_selected = True

                    if not mousebutton_pressed and any(pygame.mouse.get_pressed()):
                        mousebutton_pressed = True
                        if 0 <= index <= 2:
                            if index == 0:
                                self.scrollindex = max(0, min(self.current_state.turn - 13, self.scrollindex - 1))
                                if self.display_screen:
                                    self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                                    self.display.draw_button_overlay(self.button_rects[index])
                                    self.display.render_to_screen()
                            elif index == 1:
                                self.scrollindex = max(0, min(self.current_state.turn - 13, self.scrollindex + 1))
                                if self.display_screen:
                                    self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                                    self.display.draw_button_overlay(self.button_rects[index])
                                    self.display.render_to_screen()
                            else:
                                keepgoing = False
                else:
                    if button_selected:
                        self.display.draw_sidepanel_background()
                        self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
                        self.display.announce_winner(self.winner >= 0, self.players[self.winner].name, self.winner)
                        self.display.render_to_screen()

                        button_selected = False

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        keepgoing = False

        return self.history, self.winner

    def notify(self, event):
        if event[0] == 'scroll':
            self.scrollindex = max(0, min(self.current_state.turn - 13, self.scrollindex + event[1]))
            if self.display_screen:
                self.display.draw_history(self.history.movelist_as_string(), self.scrollindex)
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


def parse_colors(args):
    clrs = {}

    for color in args:
        (key, value) = color
        try:
            clrs[key] = literal_eval(value)
        except SyntaxError or ValueError:
            return None

    return clrs


def load_player(p, nographics):
    python_path_str = os.path.expandvars("$PYTHONPATH")
    if python_path_str.find(';') == -1:
        python_path_dirs = python_path_str.split(':')
    else:
        python_path_dirs = python_path_str.split(';')
    python_path_dirs.append('.')

    for module_dir in python_path_dirs:
        if not os.path.isdir(module_dir):
            continue

        modulenames = (file for file in os.listdir(module_dir) if
                       file.endswith('player.py') and not file.startswith('.') and not file.startswith('_'))
        for modulename in modulenames:
            try:
                module = __import__(modulename[:-3])
            except ImportError:
                continue
            if p in dir(module):
                if nographics and modulename == 'humanplayer.py':
                    raise Exception("Cannot use HumanPlayer without display")

                return getattr(module, p)

    raise Exception("The player {0} is not specified in any *player.py".format(p))


def parse_players(player_args, nographics):
    players = []
    for p in player_args:
        if '=' in p:
            key, val = p.split('=')
        else:
            key, val = "", p

        players.append((key, load_player(val, nographics)))

    return players


def parse_command_args(command_args):
    args = dict(
        disp_graphics=command_args.disp_graphics,
        switch_sides=command_args.switch_sides
    )

    # players
    # args['players'] = [load_player(p, not command_args.disp_graphics) for p in command_args.players]
    args['players'] = parse_players(command_args.players, not command_args.disp_graphics)

    return args


colors = {
    'background': (128, 128, 128, 255),
    'font': (0, 0, 0, 255),
    'square_light': (255, 238, 187, 255),
    'square_dark': (85, 136, 34, 255),
    'highlight': ((255, 0, 0, 96), (0, 0, 255, 96)),
    'piece_outline': (0, 0, 0, 255),
    'piece_light': (255, 255, 255, 255),
    'piece_dark': (64, 64, 64, 255),
    'king': (255, 0, 0, 255),
    'panelbackground': (128, 128, 128, 255),
    'buttoncolor': (192, 192, 192, 255),
    'buttonbordercolor': (64, 64, 64, 255),
    'button_highlight': (255, 128, 0, 128),
    'textcolor': (0, 0, 0, 255),
    'movelist_background': (255, 255, 255, 255)
}


def main():
    parser = argparse.ArgumentParser(description="Runs a draughts match.")

    parser.add_argument(
        '-q',
        '--quiet',
        dest='disp_graphics',
        action='store_false',
        help="Play game without graphics",
        default=True
    )
    parser.add_argument(
        '-s',
        '--switchsides',
        dest='switch_sides',
        action='store_true',
        help="Switch sides as current player changes.",
        default=False
    )
    parser.add_argument(
        '-p',
        '--players',
        dest='players',
        type=str,
        metavar='PLAYER',
        help="The player objects to be used.",
        nargs=2,
        default=['HumanPlayer', 'HumanPlayer']
    )

    command_args = parser.parse_args()
    args = parse_command_args(command_args)

    color_parser = configparser.ConfigParser()
    color_parser.read(['colors.cfg'])
    try:
        clrs = parse_colors(color_parser.items('colors'))

        if clrs:
            global colors

            for key, value in clrs.items():
                if key in colors:
                    colors[key] = value
    except configparser.NoSectionError:
        pass

    game = Game(**args)
    game.run()


if __name__ == "__main__":
    main()

import pygame


class BoardGraphics:
    def __init__(self, size, colors):
        self.size = size
        self.square_size = min(size) / 10
        self.piece_size = self.square_size * 2 / 3
        self.piece_offset = (self.square_size - self.piece_size) / 2
        self.colors = colors
        self.font = pygame.font.SysFont("inconsolata", int(self.piece_size))

    def get_board_background_surface(self):
        surf = pygame.Surface(self.size)
        surf.fill(self.colors["background"])

        for y in range(10):
            for x in range(10):
                color_index = (y + x) % 2
                if color_index == 0:
                    color = self.colors["square_light"]
                else:
                    color = self.colors["square_dark"]

                pygame.draw.rect(
                    surf,
                    color,
                    pygame.Rect(
                        self.size[0] - (10 - x) * self.square_size,
                        y * self.square_size,
                        self.square_size,
                        self.square_size
                    ),
                    0
                )

        return surf

    def __draw_piece(self, surf, pos, color, is_king):
        # outline
        pygame.draw.ellipse(
            surf,
            self.colors["piece_outline"],
            (
                pos[0],
                pos[1],
                self.piece_size,
                self.piece_size
            ),
            0
        )

        # piece color
        pygame.draw.ellipse(
            surf,
            color,
            (
                pos[0] + 1,
                pos[1] + 1,
                self.piece_size - 1,
                self.piece_size - 1
            ),
            0
        )

        # crown
        if is_king:
            pygame.draw.polygon(
                surf, self.colors["king"],
                (
                    (
                        pos[0] + self.piece_size / 5,
                        pos[1] + self.piece_size / 10 * 3
                    ),
                    (
                        pos[0] + self.piece_size / 2,
                        pos[1] + self.piece_size / 10 * 6
                    ),
                    (
                        pos[0] + self.piece_size / 5,
                        pos[1] + self.piece_size / 10 * 6
                    )
                )
            )

            pygame.draw.polygon(
                surf,
                self.colors["king"],
                (
                    (
                        pos[0] + self.piece_size / 5 * 4,
                        pos[1] + self.piece_size / 10 * 3
                    ),
                    (
                        pos[0] + self.piece_size / 2,
                        pos[1] + self.piece_size / 10 * 6
                    ),
                    (
                        pos[0] + self.piece_size / 5 * 4,
                        pos[1] + self.piece_size / 10 * 6
                    )
                )
            )

            pygame.draw.polygon(
                surf, self.colors["king"],
                (
                    (
                        pos[0] + self.piece_size / 5,
                        pos[1] + self.piece_size / 5 * 3
                    ),
                    (
                        pos[0] + self.piece_size / 2,
                        pos[1] + self.piece_size / 10 * 4
                    ),
                    (
                        pos[0] + self.piece_size / 5 * 4,
                        pos[1] + self.piece_size / 5 * 3
                    )
                )
            )

    def draw_current_player_piece(self, surf, pos, is_king, current_player):
        draw_pos = (
            self.size[0] - (10 - pos[0]) * self.square_size + self.piece_offset,
            pos[1] * self.square_size + self.piece_offset
        )

        pygame.draw.ellipse(
            surf,
            self.colors["piece_outline"],
            (
                draw_pos[0],
                draw_pos[1],
                self.piece_size,
                self.piece_size
            ),
            0
        )

        if current_player == 0:
            color = self.colors["piece_light"]
        else:
            color = self.colors["piece_dark"]

        pygame.draw.ellipse(
            surf,
            color,
            (
                draw_pos[0] + 1,
                draw_pos[1] + 1,
                self.piece_size - 1,
                self.piece_size - 1),
            0
        )

        if is_king:
            pygame.draw.polygon(
                surf, self.colors["king"],
                (
                    (
                        draw_pos[0] + self.piece_size / 5,
                        draw_pos[1] + self.piece_size / 10 * 3
                    ),
                    (
                        draw_pos[0] + self.piece_size / 2,
                        draw_pos[1] + self.piece_size / 10 * 6
                    ),
                    (
                        draw_pos[0] + self.piece_size / 5,
                        draw_pos[1] + self.piece_size / 10 * 6
                    )
                )
            )

            pygame.draw.polygon(
                surf,
                self.colors["king"],
                (
                    (
                        draw_pos[0] + self.piece_size / 5 * 4,
                        draw_pos[1] + self.piece_size / 10 * 3
                    ),
                    (
                        draw_pos[0] + self.piece_size / 2,
                        draw_pos[1] + self.piece_size / 10 * 6
                    ),
                    (
                        draw_pos[0] + self.piece_size / 5 * 4,
                        draw_pos[1] + self.piece_size / 10 * 6
                    )
                )
            )

            pygame.draw.polygon(
                surf, self.colors["king"],
                (
                    (
                        draw_pos[0] + self.piece_size / 5,
                        draw_pos[1] + self.piece_size / 5 * 3
                    ),
                    (
                        draw_pos[0] + self.piece_size / 2,
                        draw_pos[1] + self.piece_size / 10 * 4
                    ),
                    (
                        draw_pos[0] + self.piece_size / 5 * 4,
                        draw_pos[1] + self.piece_size / 5 * 3
                    )
                )
            )

    def get_piece_surface(
            self,
            player_pieces,
            opponent_pieces,
            current_player,
            switch_sides
    ):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        for index in [not current_player, current_player]:
            if index == 0:
                color = self.colors["piece_light"]
            else:
                color = self.colors["piece_dark"]

            if index == current_player:
                pieces = player_pieces
            else:
                pieces = opponent_pieces

            for piece in pieces:
                if switch_sides:
                    pos = (
                        9 - piece.pos[0],
                        9 - piece.pos[1]
                    ) if current_player else piece.pos
                else:
                    pos = piece.pos
                self.__draw_piece(
                    surf,
                    (
                        self.size[0] - (10 - pos[0]) * self.square_size
                        + self.piece_offset,
                        pos[1] * self.square_size + self.piece_offset
                    ),
                    color,
                    piece.is_king
                )

        return surf

    def get_captured_piece_surface(self, captured_pieces):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        for index in range(2):
            if index == 0:
                color = self.colors["piece_light"]
            else:
                color = self.colors["piece_dark"]

            self.__draw_piece(
                surf,
                (
                    self.piece_offset,
                    self.piece_offset + index * self.square_size
                ),
                color,
                False
            )

            (_, height) = self.font.size(str(captured_pieces[index]))
            text_surf = self.font.render(
                str(captured_pieces[index]),
                True,
                self.colors["font"]
            )
            surf.blit(
                text_surf,
                (
                    self.piece_offset + self.square_size,
                    (self.square_size - height) / 2
                    + index * self.square_size
                )
            )

        return surf

    def get_highlight_surface(self, spaces):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        for index in range(min(len(spaces), len(self.colors['highlight']))):
            for square in spaces[index]:
                (x, y) = square
                pygame.draw.rect(
                    surf,
                    self.colors['highlight'][index],
                    pygame.Rect(
                        self.size[0] - (10 - x) * self.square_size,
                        y * self.square_size,
                        self.square_size,
                        self.square_size
                    ),
                    0
                )

        return surf


class PanelGraphics:
    def __init__(self, size, colors):
        self.size = size

        self.size = size
        self.buttonsize_with_border = (size[0], size[1] / 10)
        self.button_center_offset = max(self.buttonsize_with_border) / 40
        self.buttonsize = (
            self.buttonsize_with_border[0] - 2 * self.button_center_offset,
            self.buttonsize_with_border[1] - 2 * self.button_center_offset
        )

        self.colors = colors
        self.font = pygame.font.SysFont("inconsolata",
                                        int(self.buttonsize[1] / 2))

    def get_panel_background_surface(self):
        surf = pygame.Surface(self.size)
        surf.fill(self.colors['panelbackground'])

        pygame.draw.rect(
            surf,
            self.colors['buttonbordercolor'],
            pygame.Rect(
                0,
                8 * self.buttonsize_with_border[1],
                self.buttonsize_with_border[0],
                self.buttonsize_with_border[1]
            ),
            0
        )
        pygame.draw.rect(
            surf,
            self.colors['buttoncolor'],
            pygame.Rect(
                self.button_center_offset,
                8 * self.buttonsize_with_border[1] + self.button_center_offset,
                self.buttonsize[0],
                self.buttonsize[1]
            ),
            0
        )
        (width, height) = self.font.size('Remise')
        text_surf = self.font.render('Remise', True, self.colors['textcolor'])
        surf.blit(
            text_surf,
            [
                (self.buttonsize_with_border[0] - width) / 2,
                8 * self.buttonsize_with_border[1]
                + (self.buttonsize_with_border[1] - height) / 2,
                text_surf.get_width(),
                text_surf.get_height()
            ]
        )

        pygame.draw.rect(
            surf,
            self.colors['buttonbordercolor'],
            pygame.Rect(
                0,
                9 * self.buttonsize_with_border[1],
                self.buttonsize_with_border[0],
                self.buttonsize_with_border[1]
            ),
            0
        )
        pygame.draw.rect(
            surf,
            self.colors['buttoncolor'],
            pygame.Rect(
                self.button_center_offset,
                9 * self.buttonsize_with_border[1] + self.button_center_offset,
                self.buttonsize[0],
                self.buttonsize[1]
            ),
            0
        )
        (width, height) = self.font.size('Geef op')
        text_surf = self.font.render('Geef op', True, self.colors['textcolor'])
        surf.blit(
            text_surf,
            [
                (self.buttonsize_with_border[0] - width) / 2,
                9 * self.buttonsize_with_border[1]
                + (self.buttonsize_with_border[1] - height) / 2,
                text_surf.get_width(),
                text_surf.get_height()
            ]
        )

        return surf

    def get_movelist_surface(self, movelist, scrollindex):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        pygame.draw.rect(
            surf,
            self.colors['movelist_background'],
            pygame.Rect(
                self.button_center_offset,
                self.button_center_offset,
                self.buttonsize[0],
                7 * self.buttonsize_with_border[1]
                - 2 * self.button_center_offset
            )
        )

        pygame.draw.polygon(
            surf,
            self.colors['textcolor'],
            (
                (
                    self.buttonsize[0] - 2 * self.button_center_offset,
                    3 * self.button_center_offset
                ),
                (
                    self.buttonsize[0],
                    3 * self.button_center_offset
                ),
                (
                    self.buttonsize[0] - self.button_center_offset,
                    2 * self.button_center_offset
                )
            )
        )
        pygame.draw.polygon(
            surf,
            self.colors['textcolor'],
            (
                (
                    self.buttonsize[0] - 2 * self.button_center_offset,
                    7 * self.buttonsize_with_border[1]
                    - 3 * self.button_center_offset
                ),
                (
                    self.buttonsize[0],
                    7 * self.buttonsize_with_border[1]
                    - 3 * self.button_center_offset
                ),
                (
                    self.buttonsize[0] - self.button_center_offset,
                    7 * self.buttonsize_with_border[1]
                    - 2 * self.button_center_offset
                )
            )
        )

        offset = 0
        for turn_index in range(
                max(0, scrollindex),
                min(len(movelist), scrollindex + 13)
        ):
            textsurf = self.font.render(
                "{0}. {1}".format(turn_index + 1, movelist[turn_index]),
                True,
                self.colors['textcolor']
            )
            surf.blit(
                textsurf,
                [
                    2 * self.button_center_offset,
                    3 * self.button_center_offset + offset
                    * (self.buttonsize[1] / 2 + self.button_center_offset),
                    textsurf.get_width(),
                    textsurf.get_height()
                ]
            )

            offset += 1

        return surf

    def get_consolemessage_surface(self, name, current_player, tie_request):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        player_message = '{0} is aan zet'.format(
            name
        )
        if current_player:
            color = self.colors['piece_dark']
        else:
            color = self.colors['piece_light']
        text_surf = self.font.render(player_message, True, color)
        surf.blit(
            text_surf,
            [
                (self.size[0] - text_surf.get_width()) / 2,
                7 * self.buttonsize_with_border[1],
                text_surf.get_width(),
                text_surf.get_height()
            ]
        )

        text = ""
        if tie_request == (not current_player):
            text = "Accepteer remise?"

        text_surf = self.font.render(
            text, True, self.colors['textcolor']
        )
        surf.blit(
            text_surf,
            [
                (self.size[0] - text_surf.get_width()) / 2,
                7 * self.buttonsize_with_border[1] + self.buttonsize[1] / 2
                + self.button_center_offset,
                text_surf.get_width(),
                text_surf.get_height()
            ]
        )

        return surf

    def get_highlight_button_surface(self, rect):
        size = (rect[2] - rect[0], rect[3] - rect[1])
        surf = pygame.Surface(size, pygame.SRCALPHA, 32)
        surf.fill(self.colors['button_highlight'])

        return surf

    def get_win_message_surface(self, winner_name, player_id):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        if player_id:
            color = self.colors['piece_dark']
        else:
            color = self.colors['piece_light']

        name_surf = self.font.render(winner_name, True, color)
        surf.blit(
            name_surf,
            [
                (self.size[0] - name_surf.get_width()) / 2,
                7 * self.buttonsize_with_border[1],
                name_surf.get_width(),
                name_surf.get_height()
            ]
        )

        winmessage_surf = self.font.render(
            'wint!',
            True,
            self.colors['textcolor']
        )
        surf.blit(
            winmessage_surf,
            [
                (self.size[0] - winmessage_surf.get_width()) / 2,
                7 * self.buttonsize_with_border[1] + self.buttonsize[1] / 2
                + self.button_center_offset,
                winmessage_surf.get_width(),
                winmessage_surf.get_height()
            ]
        )

        return surf

    def get_tie_message_surface(self):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        tiemessage_surf = self.font.render(
            'Remise',
            True,
            self.colors['textcolor']
        )
        surf.blit(
            tiemessage_surf,
            [
                (self.size[0] - tiemessage_surf.get_width()) / 2,
                7 * self.buttonsize_with_border[1],
                tiemessage_surf.get_width(),
                tiemessage_surf.get_height()
            ]
        )

        return surf

    def get_continuebutton_surface(self):
        surf = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        surf.fill((255, 255, 255, 0))

        pygame.draw.rect(
            surf,
            self.colors['buttonbordercolor'],
            pygame.Rect(
                0,
                8 * self.buttonsize_with_border[1],
                self.buttonsize_with_border[0],
                2 * self.buttonsize_with_border[1]
            )
        )
        pygame.draw.rect(
            surf,
            self.colors['buttoncolor'],
            pygame.Rect(
                self.button_center_offset,
                8 * self.buttonsize_with_border[1] + self.button_center_offset,
                self.buttonsize[0],
                2 * (self.buttonsize_with_border[1] - self.button_center_offset)
            )
        )
        text_surf = self.font.render(
            "Beëindig partij",
            True,
            self.colors['textcolor']
        )
        surf.blit(
            text_surf,
            [
                (self.size[0] - text_surf.get_width()) / 2,
                8 * self.buttonsize_with_border[1]
                + (2 * self.buttonsize_with_border[1] - text_surf.get_height())
                / 2,
                text_surf.get_width(),
                text_surf.get_height()
            ]
        )

        return surf

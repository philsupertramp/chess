from typing import List, Optional, Tuple

import pygame

from src.backends.colors import BLACK, WHITE
from src.figures import Figure, King, Queen, Knight, Pawn, Bishop, Rook
from src.helpers import sign
from src.history import TurnHistory


class CheckerBoard:
    fields: List[List[Optional[Figure]]] = list(list())

    def __init__(self, display: pygame.Surface, game) -> None:
        # Game state
        self.game = game
        # Texture for simple rendering
        self.empty_board: Optional[pygame.Surface] = None
        # cell height and width
        self.cell_size: Optional[Tuple[int]] = None
        # pointer to currently selected figure
        self.selected_figure = None
        # initial canvas
        self.canvas = display
        # actual game state
        self.fields: List[List[Optional[Figure]]] = list()

        if self.game.use_pygame:
            self.init_empty_field_texture()

        self.reset()

    def rescale(self, canvas: pygame.Surface) -> None:
        self.canvas = canvas
        self.init_empty_field_texture()

    def get_figures(self, type_val: int) -> List[Figure]:
        """
        Getter for figures by type value
        :param type_val:
        :return:
        """
        figures = list()
        for col in self.fields:
            for cell in col:
                if cell and cell.type == type_val:
                    figures.append(cell)
        return figures

    def reset(self) -> None:
        """
        Resets board content

        some examples:

        only pawns and kings: '4k/PPPPPPPP/8/8/8/8/pppppppp/4K'
        castling: 'r3k2r/8/8/8/8/8/8/R3K2R'
        """
        self.fields = [[None for _ in range(8)] for _ in range(8)]
        self.load_game_from_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')

    def reset_en_passant(self, is_white: bool) -> None:
        """
        Resets en-passant pawn state for given color
        :param is_white: color to clean
        """
        for col in self.fields:
            for cell in col:
                if cell and cell.is_white == is_white and cell.en_passant:
                    cell.en_passant = False

    def reset_castles(self, is_white: bool) -> None:
        """
        Resets game state for castled kings
        :param is_white: color to clean
        """
        for col in self.fields:
            for cell in col:
                if cell and cell.is_white == is_white and cell.castles_with:
                    cell.castles_with = None

    def init_empty_field_texture(self, with_text: bool = True) -> None:
        """
        Initializes empty checkerboard texture.

        Actually only renders black tiles on white background
        """

        # convert board size to cell size
        self.cell_size = self.canvas.get_width() / 8, self.canvas.get_height() / 8

        # create an empty surface and paint it white
        self.empty_board = pygame.Surface((self.cell_size[0] * 8, self.cell_size[1] * 8))
        self.empty_board.fill(WHITE)

        def get_elem_rect(_x, _y):
            """Helper method to get scaled coordinates"""
            return _x * self.cell_size[0], _y * self.cell_size[1], self.cell_size[0], self.cell_size[1]

        for x in range(1, 8, 2):
            for y in range(1, 8, 2):
                pygame.draw.rect(self.empty_board, BLACK, get_elem_rect(x, y))
        for x in range(0, 8, 2):
            for y in range(0, 8, 2):
                pygame.draw.rect(self.empty_board, BLACK, get_elem_rect(x, y))

        if with_text:
            from src.backends.screen import screen
            for x in range(8):
                for y in range(8):
                    screen.draw_text_to_surface(TurnHistory.pos_to_string((x, y)), (x * self.cell_size[0], y * self.cell_size[1]), self.empty_board)

    def load_game_from_string(self, input_string: str) -> None:
        """do some magic input string parsing

        available types
        k: king
        q: queen
        n: knight
        p: pawn
        b: bishop
        r: rook

        Example:
            initial setup:
            rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR

        :param input_string: input string "/"-separated
        """
        for row, element in enumerate(input_string.split('/')):
            index = 0
            col = 0
            while index < len(element):
                try:
                    col += int(element[index]) + 1
                    index += 1
                except ValueError:
                    if col == 8:
                        col = 0
                    else:
                        col += 1

                try:
                    figure_type = element[index]
                except IndexError:
                    # found empty line
                    continue

                is_white = figure_type.isupper()
                figure_class = None
                if figure_type.lower() == 'k':
                    figure_class = King
                elif figure_type.lower() == 'q':
                    figure_class = Queen
                elif figure_type.lower() == 'n':
                    figure_class = Knight
                elif figure_type.lower() == 'p':
                    figure_class = Pawn
                elif figure_type.lower() == 'b':
                    figure_class = Bishop
                elif figure_type.lower() == 'r':
                    figure_class = Rook

                self.fields[row][col-1] = figure_class((col-1, row), is_white=is_white, _board=self)
                index += 1

    def draw(self) -> None:
        """
        Renders the board into the global window.

        Renders board texture and skips empty fields for efficiency.
        """
        from src.backends.screen import screen
        self.canvas.blit(self.empty_board, self.empty_board.get_rect())

        for x in range(len(self.fields)):
            for y in range(len(self.fields[x])):
                if not self.fields[x][y]:
                    continue

                self.fields[x][y].draw(self.canvas)

        screen.blit(self.canvas, self.canvas.get_rect())

    def handle_figure_selection(self, cols: int, rows: int, is_white_turn: bool) -> None:
        """
        Handles selection of a figure

        Call to select a figure to given position.

        :param cols: selected column
        :param rows: selected row
        :param is_white_turn:
        """
        self.selected_figure = self.fields[rows][cols]
        # only allow selection if its the players turn
        if self.selected_figure:
            if self.selected_figure.is_white == is_white_turn:
                # successfully selected figure
                self.fields[rows][cols].is_selected = True
            else:
                # unselect figure and print a picking error
                color = "White" if is_white_turn else "Black"
                print(f'{color} tried selecting {self.selected_figure}, not allowed.')
                # reset picked figure
                self.selected_figure = None

    def handle_figure_placement(self, cols: int, rows: int, is_white_turn: bool) -> bool:
        """
        Handles figure placement in board

        Call to place a figure to the given position.
        :param cols: selected column
        :param rows:  selected row
        :param is_white_turn:
        :return: placement successful
        """
        old_pos = self.selected_figure.position

        if old_pos != (cols, rows) and self.selected_figure.move((cols, rows)):
            prev_fig_pos = (rows, cols)
            # en-passant
            if self.selected_figure.checked_en_passant:
                prev_fig_pos = (old_pos[1], prev_fig_pos[1])
            # castling
            elif self.selected_figure.castles_with is not None:
                prev_fig_pos = self.selected_figure.castles_with.position

            prev_fig = self.fields[prev_fig_pos[0]][prev_fig_pos[1]]
            self.selected_figure.checked_en_passant = False
            self.game.history.record(self.selected_figure, old_pos, (cols, rows), prev_fig)
            if prev_fig and prev_fig.checkmate():
                self.game.running = False
                print(f'Game over {"white" if is_white_turn else "black"} wins.')

            if self.selected_figure.castles_with:
                # perform switch during castling
                direction = sign(self.selected_figure.position[0] - old_pos[0])
                self.fields[old_pos[1]][cols - 2 * direction] = self.selected_figure.castles_with
                self.selected_figure.castles_with.position = (cols - 2 * direction, old_pos[1])
                cols -= direction

            self.fields[old_pos[1]][old_pos[0]] = None
            self.fields[prev_fig_pos[0]][prev_fig_pos[1]] = None
            self.selected_figure.position = (cols, rows)
            self.fields[rows][cols] = self.selected_figure

            if hasattr(self.selected_figure, 'needs_render_selector'):
                self.game.needs_render_selector = self.selected_figure.board.needs_render_selector
                # always delete the temporary value. aint no snitch, but try keepin it immutable, fam
                del self.selected_figure.board.needs_render_selector

        else:
            print(f'Tried moving {self.selected_figure} -> {(cols, rows)}, not allowed.')
            return False

        self.fields[self.selected_figure.position[1]][self.selected_figure.position[0]].is_selected = False
        if not self.game.needs_render_selector:
            self.selected_figure = None

        self.reset_en_passant(not is_white_turn)
        self.reset_castles(not is_white_turn)
        return True

    def handle_figure_promotion(self, cols: int, rows: int) -> None:
        """
        Handles Pawn-promotion in place.

        :param cols: selected column
        :param rows: selected row
        """
        if rows > 1 or cols > 1:
            print('Error selecting...\nRetry!')
        fig_class = self.game.figure_selector.select(rows * 2 + cols)
        figure = fig_class(self.selected_figure.position, is_white=self.selected_figure.is_white, _board=self.board)

        # figure.has_moved disables/enables Rook's castling mechanics
        figure.has_moved = not self.game.underpromoted_castling
        self.fields[self.selected_figure.position[1]][self.selected_figure.position[0]] = figure
        self.selected_figure = None
        self.game.backend.needs_render_selector = False
        self.game.is_white_turn = not self.game.is_white_turn

    def handle_mouse_click(self, cols: int, rows: int, is_white_turn: bool) -> bool:
        """
        Handles mouse click from game

        returns indicator for color turn change
        :param cols: clicked col
        :param rows: clicked row
        :param is_white_turn: current players turn is white
        :return: change in turn
        """

        if not self.selected_figure:
            self.handle_figure_selection(cols, rows, is_white_turn)
            return False
        else:
            return self.handle_figure_placement(cols, rows, is_white_turn)

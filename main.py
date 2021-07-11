
import pygame

from src.screen import screen

from src.history import TurnHistory
from typing import List, Optional, Tuple

from src.figures import Figure, King, Queen, Pawn, Bishop, Rook, Knight, rescale_images


BLACK = pygame.color.Color(103,	114, 136, 50)
WHITE = pygame.color.Color(255, 255, 255, 255)


rescale_images(screen)


class CheckerBoard:
    fields: List[List[Optional[Figure]]] = list(list())
    field_objects: List = list()
    elem_width: int = 0
    elem_height: int = 0

    def __init__(self, display):
        self.empty_board: Optional[pygame.Surface] = None
        self.cell_size: Optional[Tuple[int]] = None
        self.canvas = display
        self.init_empty_field()

        self.fields: List[List[Optional[Figure]]] = [[None for _ in range(8)] for _ in range(8)]

        self.load_game_from_string('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR')

    def init_empty_field(self):
        self.cell_size = self.canvas.get_width() / 8, self.canvas.get_height() / 8
        self.empty_board = pygame.Surface((self.cell_size[0] * 8, self.cell_size[1] * 8))
        self.empty_board.fill((255, 255, 255))

        def get_elem_rect(_x, _y):
            return _x * self.cell_size[0], _y * self.cell_size[1], self.cell_size[0], self.cell_size[1]

        for x in range(1, 8, 2):
            for y in range(1, 8, 2):
                pygame.draw.rect(self.empty_board, BLACK, get_elem_rect(x, y))
        for x in range(0, 8, 2):
            for y in range(0, 8, 2):
                pygame.draw.rect(self.empty_board, BLACK, get_elem_rect(x, y))

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
        :returns: None
        """
        for row, element in enumerate(input_string.split('/')):
            index = 0
            col = 0
            while index < len(element):
                try:
                    col = int(element[index]) - 1
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

    def draw(self):
        self.canvas.blit(self.empty_board, self.empty_board.get_rect())

        for x in range(len(self.fields)):
            for y in range(len(self.fields[x])):
                if not self.fields[x][y]:
                    continue

                self.fields[x][y].draw(self.canvas)

        screen.blit(self.canvas, self.canvas.get_rect())


if __name__ == '__main__':
    canvas = pygame.Surface((screen.get_size()[0], screen.get_size()[1] - 20))
    board = CheckerBoard(canvas)
    history = TurnHistory()
    selected_figure = None
    is_mouse_clicked = False
    running = True
    is_white_turn = True
    while running:
        screen.fill((255, 255, 255))
        board.draw()
        text = f'{"Whites" if is_white_turn else "Blacks"} turn'
        screen.draw_text(text, (screen.get_width()/2, screen.get_height() - 15))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.K_ESCAPE:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            if event.type == pygame.WINDOWSIZECHANGED:
                canvas = pygame.Surface((screen.get_width(), screen.get_height() - 20))
                rescale_images(canvas)
                board.canvas = canvas
                board.init_empty_field()

            if not is_mouse_clicked:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    is_mouse_clicked = True

                    mouse_pos = pygame.mouse.get_pos()
                    scale = screen.get_width() / 8, (screen.get_height() - 20) / 8
                    cols = int(mouse_pos[0] / scale[0])
                    rows = int(mouse_pos[1] / scale[1])

                    if not selected_figure:
                        selected_figure = board.fields[rows][cols]
                        # only allow selection if its the players turn
                        if selected_figure:
                            if selected_figure.is_white == is_white_turn:
                                board.fields[rows][cols].is_selected = True
                            else:
                                color = "White" if is_white_turn else "Black"
                                print(f'{color} tried selecting {selected_figure}, not allowed.')
                                selected_figure = None
                    else:
                        old_pos = selected_figure.position
                        if selected_figure.move((cols, rows)):
                            prev_fig = board.fields[rows][cols]
                            history.record(selected_figure, (rows, cols), prev_fig)
                            if prev_fig and prev_fig.checkmate():
                                running = False
                                print(f'Game over {"white" if is_white_turn else "black"} wins.')
                            board.fields[old_pos[1]][old_pos[0]] = None
                            board.fields[rows][cols] = selected_figure
                            selected_figure = None

                            # switch turn
                            is_white_turn = not is_white_turn
                        else:
                            print(f'Tried moving {selected_figure} -> {(cols, rows)}, not allowed.')
                            selected_figure = None

            if event.type == pygame.MOUSEBUTTONUP:
                is_mouse_clicked = False

    pygame.quit()

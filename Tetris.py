import json
from copy import deepcopy

import pygame
import random


class Scheduler:
    def __init__(self):
        self.dict = dict()

    def do_tick(self):
        for i in range(len(self.dict) - 1, -1, -1):
            func = list(self.dict.keys())[i]
            ticks = self.dict[i]
            if ticks == 1:
                func()
                self.dict.pop(i)
                continue
            self.dict[func] = ticks - 1

    def add_task(self, func, ticks):
        self.dict[func] = ticks


class Board:
    def __init__(self, count_x, count_y, size_cell, color):
        self.count_x = count_x
        self.count_y = count_y
        self.size_cell = size_cell
        self.color = color
        self.board = [[[] for y in range(count_y)] for x in range(count_x)]

    def render(self, surface: pygame.Surface):
        for x in range(self.count_x):
            for y in range(self.count_y):
                sc = self.size_cell
                pygame.draw.rect(surface, self.color, (x * sc, y * sc, sc, sc))
                color_in = self.board[x][y]
                if not color_in:
                    color_in = [0] * 3
                pygame.draw.rect(surface, color_in, (x * sc + 1, y * sc + 1, sc - 2, sc - 2))


class Tetris:
    def __init__(self, WIDTH, HEIGHT, FPS, board_data):
        """board_data = [count_x: int, count_y: int, size_cell: int, color: list[int, int, int]]"""
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.FPS = FPS
        self.board_data = board_data
        self.init_pygame()
        self.extra_init()
        new_or_old = StartWindow(WIDTH, HEIGHT).open()
        self.start_game_loop()

    def init_pygame(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.display = pygame.display
        self.display.init()
        self.display.set_mode((self.WIDTH, self.HEIGHT))
        self.display.set_caption("Tetris by mrfix1033")
        self.surface = self.display.get_surface()

    def extra_init(self):
        self.running = True
        self.board = Board(*self.board_data)
        self.figures_handler = FiguresHandler(self.board)
        self.timer = Scheduler()

    def start_game_loop(self):
        while self.running:
            self.clock.tick(self.FPS)
            self.do_tick()
            self.extra_do_tick()

    def do_tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.K_a:
                self.figures_handler.select_figure.left_move()
            elif event.type == pygame.K_s:
                self.figures_handler.select_figure.down_move()
            elif event.type == pygame.K_d:
                self.figures_handler.select_figure.right_move()
            elif event.type == pygame.K_q:
                self.figures_handler.select_figure.rotate(Figure.ROTATE_LEFT)
            elif event.type == pygame.K_e:
                self.figures_handler.select_figure.rotate(Figure.ROTATE_RIGHT)

    def extra_do_tick(self):
        self.timer.do_tick()
        self.figures_handler.do_big_tick()
        self.board.render(self.surface)
        pygame.display.flip()


class Main:
    def __init__(self):
        SCALE = 1
        FPS = 60
        count_x = 10
        count_y = 20
        size_cell = 30
        color = [42] * 3
        size_cell_scaled = size_cell * SCALE
        WIDTH, HEIGHT = count_x * size_cell_scaled, count_y * size_cell_scaled
        board_data = [count_x, count_y, size_cell_scaled, color]
        self.data_handler = DataHandler()
        self.game = Tetris(WIDTH, HEIGHT, FPS, board_data)


class StartWindow:
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.screen = pygame.Surface((self.WIDTH, self.HEIGHT))
        pygame.font.init()

    def open(self):
        tetris_surface = main.game.surface
        space_was_clicked = False
        while True:
            for e in pygame.event.get():
                if e.type == pygame.K_UP:
                    if e.key == pygame.K_SPACE and not space_was_clicked:
                        space_was_clicked = True
                        data_game = main.data_handler.get_data_game()
                        if not data_game:
                            return
                    elif space_was_clicked:
                        if e.key == pygame.K_O:
                            # data_game к моменту использования будет объявленна
                            main.game.board = data_game[0]
                            main.game.figures_handler.select_figure = data_game[1]
                            main.game.figures_handler.color_now = data_game[2]
                            main.game.score = data_game[3]
            start_surface = pygame.Surface((main.game.WIDTH, main.game.HEIGHT))
            if not space_was_clicked:  # самый начальный экран
            else:
                font = pygame.font.Font("Intro", 20)
                titles = [font.render("Вы не завершили прошлую игру", True, [255] * 3),
                font.render("Чтобы её продолжить нажмите O (англ.)", True, [255] * 3),
                font.render("Чтобы начать новую нажмите N", True, [255] * 3)]
                for i in range()


            tetris_surface.blit(start_surface, (0, 0))
            pygame.display.flip()




class DataHandler:
    def __init__(self):
        with open("data.txt", encoding='utf8') as file:
            self.dict = eval(file.read())

    def get_data_game(self):
        """возращает данные по предыдущей игре если прошлая игра не была завершена, иначе []"""
        return self.dict.get('data_game', [])

    def save_game(self, board_without_select_figure, select_figure, select_figure_color, score):
        # example: save_game(board_without_select_figure, [[1, 1], [1, 1]], [255, 0, 255], 30)
        with open("data.txt", encoding='utf8') as file:
            file.write(str([board_without_select_figure, select_figure, select_figure_color, score]))


class FiguresHandler:
    def __init__(self, board):
        self.board = board
        self.O = Figure([[1, 1],
                         [1, 1]], self.board)
        self.I = Figure([[1],
                         [1],
                         [1],
                         [1]], self.board)
        self.S = Figure([[1, 0],
                         [1, 1],
                         [0, 1]], self.board)
        self.Z = Figure([[0, 1],
                         [1, 1],
                         [1, 0]], self.board)
        self.L = Figure([[1, 0],
                         [1, 0],
                         [1, 1]], self.board)
        self.J = Figure([[0, 1],
                         [0, 1],
                         [1, 1]], self.board)
        self.T = Figure([[1, 1, 1],
                         [0, 1, 0]], self.board)
        self.figures = [self.O, self.I, self.S, self.Z, self.L, self.J, self.T]
        self.create()

    def create(self):
        self.select_figure = deepcopy(random.choice(self.figures))
        self.color_now = [random.randint(0, 255) for i in range(3)]

    def do_big_tick(self):
        figure_has_moved = self.select_figure.down_move()
        if figure_has_moved:
            return
        self.create()


class Figure:
    ROTATE_LEFT = -1
    ROTATE_RIGHT = 1

    def __init__(self, schem, board):
        self.schem = schem
        self.board = board
        self.old_render = []
        self.uncompress()
        self.coords = [self.board.WIDTH // 2 - len(self.schem[0]), 0]
        self.collide_setup()

    def collide_setup(self):
        self.down_collide_cells = [0] * len(self.schem[0])
        for column in range(len(self.schem[0])):
            for string in range(len(self.schem)):
                if self.schem[string][column]:
                    self.down_collide_cells[column] = string
        self.right_collide_cells = [0] * len(self.schem)
        for string in range(len(self.schem)):
            for column in range(len(self.schem[0])):
                if self.schem[string][column]:
                    self.right_collide_cells[string] = column
        self.left_collide_cells = [len(self.schem[0]) - 1] * len(self.schem)
        for string in range(len(self.schem)):
            for column in range(len(self.schem[0]) - 1, -1, -1):
                if self.schem[string][column]:
                    self.right_collide_cells[string] = column

    def compress(self):
        """максимально сжимает схему фигуры"""
        self.schem = deepcopy(self.rotate_schem)
        column_indexes = [any(string[column] for string in self.schem) for column in range(len(self.schem))]
        str_indexes = [any(string) for string in self.schem]
        for str_index in range(len(str_indexes) - 1, -1, -1):
            if not str_indexes[str_index]:
                self.schem.pop(str_index)
            if not column_indexes[str_index]:
                for column_index in self.schem:
                    column_index.pop(str_index)

    def uncompress(self):
        """дополняет схему фигуры по сторонам, чтобы она была квадратной"""
        self.rotate_schem = deepcopy(self.schem)
        max_len = max(len(self.rotate_schem), len(self.rotate_schem[0]))
        if len(self.rotate_schem) > len(self.rotate_schem[0]):
            need_add = (max_len - len(self.rotate_schem[0]))
            need_add_before = need_add // 2
            need_add_after = need_add - need_add_before
            for column in range(len(self.rotate_schem)):
                self.rotate_schem[column] = [0] * need_add_before + \
                                            self.rotate_schem[column] + \
                                            [0] * need_add_after
        else:
            self.rotate_schem += [[0] * len(self.rotate_schem[0])
                                  for i in range(max_len - len(self.rotate_schem))]

    def rotate(self, ROTATE):
        old_schemas = [deepcopy(self.schem), deepcopy(self.rotate_schem)]
        length = len(self.rotate_schem)
        new_schem = deepcopy(self.rotate_schem)
        for x in range(length):
            for y in range(length):
                if ROTATE == self.ROTATE_RIGHT:
                    new_schem[length - y - 1, x] = self.rotate_schem[x][y]
                else:
                    new_schem[y, length - x - 1] = self.rotate_schem[x][y]
        self.rotate_schem = new_schem
        self.compress()
        if self.coords[0] + len(self.schem[0]) > self.board.WIDTH:
            self.coords[0] = self.board.WIDTH - len(self.schem[0])
        for y in range(len(self.schem)):
            for x in range(len(self.schem[0])):
                if self.schem[y][x]:
                    x += self.coords[0]
                    y += self.coords[1]
                    if self.board[x, y]:
                        self.schem, self.rotate_schem = old_schemas
                        break

    def clear_rendered(self):
        for x, y in self.old_render:
            self.board[x][y] = []
        self.old_render = []

    def render_to_board(self):
        self.clear_rendered()
        for y in range(len(self.schem)):
            for x in range(len(self.schem[0])):
                if self.schem[y][x]:
                    x += self.coords[0]
                    y += self.coords[1]
                    self.board[x, y] = main.game.figures_handler.color_now
                    self.old_render.append((x, y))

    def down_move(self):
        """двигает фигуру вниз, если фигура не была сдвинута, вернет False, иначе True"""
        if self.check_down_move():
            self.coords[1] += 1
            return True
        return False

    def right_move(self):
        """двигает фигуру вправо"""
        if self.check_right_move():
            self.coords[0] += 1

    def left_move(self):
        """двигает фигуру влево"""
        if not self.check_left_move():
            self.coords[0] -= 1

    def check_down_move(self):
        """проверяется место под фигурой при down_move
        True - если есть место, False - если нет места"""
        if len(self.schem) + self.coords[1] > self.board.HEIGHT:
            return False
        coords_copy = self.coords.copy()
        for y in self.down_collide_cells:
            coords_copy[0] += 1
            coords_copy[1] = self.coords[1] + y + 1
            if self.board[coords_copy[0], coords_copy[1]]:
                return False
        return True  # move after rotate if figure out of bound. and for down_move cancel move

    def check_right_move(self):
        """проверяется место справа от фигуры при right_move
        True - если есть место, False - если нет места"""
        if len(self.schem[0]) + self.coords[0] > self.board.WIDTH:
            return False
        coords_copy = self.coords.copy()
        for y in self.down_collide_cells:
            coords_copy[0] += 1
            coords_copy[1] = self.coords[1] + y + 1
            if self.board[coords_copy[0], coords_copy[1]]:
                return False
        return True

    def check_left_move(self):
        """проверяется место слева от  фигуры при left_move
        True - если есть место, False - если нет места"""
        if self.coords[0] == 0:
            return False
        coords_copy = self.coords.copy()
        for y in self.down_collide_cells:
            coords_copy[0] += 1
            coords_copy[1] = self.coords[1] + y + 1
            if self.board[coords_copy[0], coords_copy[1]]:
                return False
        return True

    def copy(self):
        return Figure(self.schem, self.board)


main = Main()

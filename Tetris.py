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
        self.start_window = StartWindow(WIDTH, HEIGHT)
        self.game = Tetris(WIDTH, HEIGHT, FPS, board_data)


class StartWindow:
    def __init__(self):
        self.screen = pygame.Surface()


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
        self.select_figure = random.choice(self.figures).copy()
        self.color = [random.randint(0, 255) for i in range(3)]

    def do_big_tick(self):
        self.select_figure.down_move()


class Figure:

    ROTATE_LEFT = -1
    ROTATE_RIGHT = 1

    def __init__(self, schem, board):
        self.schem = schem
        self.board = board
        self.uncompress()
        self.coords = []

    def compress(self):
        l_indexes = [all() for i in range()]

    def uncompress(self):
        max_len = max(len(self.schem), len(self.schem[0]))
        if len(self.schem) > len(self.schem[0]):
            need_add = (max_len - len(self.schem[0]))
            need_add_before = need_add // 2
            need_add_after = need_add - need_add_before
            for i in range(len(self.schem)):
                self.schem[i] = [0] * need_add_before + self.schem[i] + [0] * need_add_after
        else:
            self.schem += [[0] * len(self.schem[0]) for i in range(max_len - len(self.schem))]


    def rotate(self, ROTATE):
        length = len(self.rotate_schem)
        new_schem = deepcopy(self.rotate_schem)
        for x in range(length):
            for y in range(length):
                if ROTATE == self.ROTATE_RIGHT:
                    new_schem[length - y - 1, x] = self.rotate_schem[x][y]
                else:
                    new_schem[y, length - x - 1] = self.rotate_schem[x][y]

    def render_to_board(self):
        pass

    def down_move(self):
        pass

    def right_move(self):
        pass

    def left_move(self):
        pass

    def copy(self):
        return Figure(self.schem, self.board)


main = Main()

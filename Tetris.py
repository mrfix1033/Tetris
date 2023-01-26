import os.path
import sys
from copy import deepcopy

import pygame
import random


class Scheduler:
    def __init__(self):
        self.keys = list()
        self.values = list()

    def do_tick(self):
        for i in range(len(self.keys) - 1, -1, -1):
            func = list(self.keys)[i]
            ticks = self.values[i]
            if ticks == 1:
                func()
                self.keys.pop(i)
                self.values.pop(i)
                continue
            self.values[i] -= 1

    def add_task(self, func, ticks):
        self.keys.append(func)
        self.values.append(ticks)


class Board:
    def __init__(self, count_x, count_y, size_cell, color):
        self.count_x = count_x
        self.count_y = count_y
        self.size_cell = size_cell
        self.color = color
        self.board = [[[] for _ in range(count_y)] for _ in range(count_x)]

    def render(self, surface: pygame.Surface):
        sc = self.size_cell
        for x in range(self.count_x):
            for y in range(self.count_y):
                pygame.draw.rect(surface, self.color, (x * sc, y * sc, sc, sc))
                color_in = self.board[x][y]
                if not color_in:
                    color_in = [0] * 3
                pygame.draw.rect(surface, color_in, (x * sc + 1, y * sc + 1, sc - 2, sc - 2), 0)
        pygame.draw.rect(surface, "red", (0, sc * main.game.line_level, sc * self.count_x, 2))


class Tetris:
    def __init__(self, WIDTH, HEIGHT, FPS, board_data):
        """board_data = [count_x: int, count_y: int, size_cell: int, color: list[int, int, int]]"""
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.FPS = FPS
        self.board_data = board_data

    def start_init(self):
        self.init_pygame()
        self.extra_init()
        StartWindow(self.WIDTH, self.HEIGHT).open()
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
        self.score = 0
        self.line_level = 4
        self.running = True
        self.board = Board(*self.board_data)
        self.figures_handler = FiguresHandler()
        self.scheduler = Scheduler()

    def start_game_loop(self):
        def start():
            self.figures_handler.do_big_tick()
            self.scheduler.add_task(start, self.FPS)

        self.start = start
        self.start()
        while self.running:
            self.clock.tick(self.FPS)
            self.do_tick()
            self.extra_do_tick()

    def do_tick(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.figures_handler.select_figure.left_move()
                elif event.key == pygame.K_s:
                    self.figures_handler.select_figure.down_move()
                elif event.key == pygame.K_d:
                    self.figures_handler.select_figure.right_move()
                elif event.key == pygame.K_q:
                    self.figures_handler.select_figure.rotate(Figure.ROTATE_LEFT)
                elif event.key == pygame.K_e:
                    self.figures_handler.select_figure.rotate(Figure.ROTATE_RIGHT)
        self.figures_handler.select_figure.render_to_board()

    def extra_do_tick(self):
        self.scheduler.do_tick()
        self.board.render(self.surface)
        pygame.display.flip()

    def lose(self):
        self.running = False
        LoseWindow()


class Main:
    def start(self):
        SCALE = 1
        FPS = 60
        count_x = 10 // 2 + 1
        count_y = 20 // 2
        size_cell = 30
        color = [42] * 3
        size_cell_scaled = size_cell * SCALE
        WIDTH, HEIGHT = count_x * size_cell_scaled, count_y * size_cell_scaled
        board_data = [count_x, count_y, size_cell_scaled, color]
        self.data_handler = DataHandler()
        self.game = Tetris(WIDTH, HEIGHT, FPS, board_data)
        self.game.start_init()


class Window:
    def __init__(self, WIDTH, HEIGHT):
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.screen = pygame.Surface((self.WIDTH, self.HEIGHT))
        pygame.font.init()

    def open(self):
        pass

class EndWindow(Window):
    def __init__(self, WIDTH, HEIGHT):
        super().__init__(WIDTH, HEIGHT)
    
    def open(self):  # todo
        tetris_surface = main.game.surface
        space_was_clicked = False
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE and not space_was_clicked:
                        space_was_clicked = True
                        data_game = main.data_handler.get_data_game()
                        if not data_game:
                            return
                    elif space_was_clicked:
                        if e.key == pygame.K_O:
                            # data_game к моменту использования будет объявленна
                            main.game.board = data_game[0]
                            figure = Figure(data_game[1])
                            figure.coords = data_game[2]
                            main.game.figures_handler.select_figure = figure
                            main.game.figures_handler.color_now = data_game[3]
                            main.game.score = data_game[4]
                        elif e.key == pygame.K_N:
                            return
            font_size = 30
            font_name = pygame.font.get_default_font()  # pygame.font.match_font("Intro", False, False)

            font = pygame.font.Font(font_name, font_size)
            if not space_was_clicked:  # самый начальный экран
                titles = [font.render("TETRIS", True, [255] * 3),
                          font.render("Нажмите пробел", True, [255] * 3),
                          font.render("для начала игры", True, [255] * 3)]
                center = self.WIDTH // 2, self.HEIGHT // 2
                for i in range(len(titles)):
                    title = titles[i]
                    tetris_surface.blit(title,
                                        (center[0] - title.get_width() // 2,
                                         center[1] - (font_size * 1.5 * (len(titles) - i - 2))
                                         - title.get_height() // 2))
            else:
                titles = [font.render("Вы не завершили прошлую игру", True, [255] * 3),
                          font.render("Чтобы её продолжить нажмите O (англ.)", True, [255] * 3),
                          font.render("Чтобы начать новую нажмите N", True, [255] * 3)]
                center = tetris_surface.get_width() // 2, tetris_surface.get_height() // 2
                for i in range(len(titles)):
                    title = titles[i]
                    tetris_surface.blit(title,
                                        (center[0] - title.get_width() // 2,
                                         font_size * 2 * (i + 1) + center[1] - title.get_height() // 2))
            pygame.display.flip()


class StartWindow(Window):
    def __init__(self, WIDTH, HEIGHT):
        super().__init__(WIDTH, HEIGHT)

    def open(self):
        tetris_surface = main.game.surface
        space_was_clicked = False
        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    sys.exit()
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_SPACE and not space_was_clicked:
                        space_was_clicked = True
                        data_game = main.data_handler.get_data_game()
                        if not data_game:
                            return
                    elif space_was_clicked:
                        if e.key == pygame.K_O:
                            # data_game к моменту использования будет объявленна
                            main.game.board = data_game[0]
                            figure = Figure(data_game[1])
                            figure.coords = data_game[2]
                            main.game.figures_handler.select_figure = figure
                            main.game.figures_handler.color_now = data_game[3]
                            main.game.score = data_game[4]
                        elif e.key == pygame.K_N:
                            return
            font_size = 30
            font_name = pygame.font.get_default_font()  # pygame.font.match_font("Intro", False, False)

            font = pygame.font.Font(font_name, font_size)
            if not space_was_clicked:  # самый начальный экран
                titles = [font.render("TETRIS", True, [255] * 3),
                          font.render("Нажмите пробел", True, [255] * 3),
                          font.render("для начала игры", True, [255] * 3)]
                center = self.WIDTH // 2, self.HEIGHT // 2
                for i in range(len(titles)):
                    title = titles[i]
                    tetris_surface.blit(title,
                                        (center[0] - title.get_width() // 2,
                                         center[1] - (font_size * 1.5 * (len(titles) - i - 2))
                                         - title.get_height() // 2))
            else:
                titles = [font.render("Вы не завершили прошлую игру", True, [255] * 3),
                          font.render("Чтобы её продолжить нажмите O (англ.)", True, [255] * 3),
                          font.render("Чтобы начать новую нажмите N", True, [255] * 3)]
                center = tetris_surface.get_width() // 2, tetris_surface.get_height() // 2
                for i in range(len(titles)):
                    title = titles[i]
                    tetris_surface.blit(title,
                                        (center[0] - title.get_width() // 2,
                                         font_size * 2 * (i + 1) + center[1] - title.get_height() // 2))
            pygame.display.flip()


class DataHandler:
    def __init__(self):
        self.create_if_not_exists("data.txt")
        with open("data.txt", encoding='utf8') as file:
            read = file.read()
        try:
            self.dict = eval(read)
        except:
            self.exception("data.txt")
            with open("config.txt", 'w', encoding='utf8') as file:
                file.write("{}")

    def create_if_not_exists(self, filename, s_if_not_exists='{}'):
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf8') as file:
                file.write(s_if_not_exists)

    def exception(self, filename):
        print(f"Возникла ошибка, файл {filename} был сброшен")

    def get_data_game(self):
        """возращает данные по предыдущей игре если прошлая игра не была завершена, иначе []"""
        return self.dict.get('data_game', [])

    def save_game(self, board_without_select_figure, select_figure, select_figure_color, score):
        # example: save_game(board_without_select_figure, [[1, 1], [1, 1]], [255, 0, 255], 30)
        with open("data.txt", encoding='utf8') as file:
            file.write(str([board_without_select_figure, select_figure.schem, select_figure.coords,
                            select_figure_color, score]))


class FiguresHandler:
    def __init__(self):
        self.O = Figure([[1, 1],
                         [1, 1]])
        self.I = Figure([[1],
                         [1],
                         [1],
                         [1]])
        self.S = Figure([[1, 0],
                         [1, 1],
                         [0, 1]])
        self.Z = Figure([[0, 1],
                         [1, 1],
                         [1, 0]])
        self.L = Figure([[1, 0],
                         [1, 0],
                         [1, 1]])
        self.J = Figure([[0, 1],
                         [0, 1],
                         [1, 1]])
        self.T = Figure([[1, 1, 1],
                         [0, 1, 0]])
        self.figures = [self.O]  # , self.I, self.S, self.Z, self.L, self.J, self.T]
        self.create()

    def create(self):
        self.select_figure = random.choice(self.figures).copy()
        self.color_now = [random.randint(0, 255) for _ in range(3)]

    def do_big_tick(self):
        figure_has_moved = self.select_figure.down_move()
        self.select_figure.render_to_board()
        if figure_has_moved:
            return
        board = main.game.board
        for x in range(board.count_x):
            if board.board[x][main.game.line_level - 1]:
                main.game.lose()
        strs = []
        for y in range(board.count_y):
            for x in range(board.count_x):
                if not board.board[x][y]:
                    break
            else:
                strs.append(y)
        if not strs:
            self.create()
            return
        # моргание линии и дальнейший сдвиг всех фигур вниз
        old_FPS = main.game.FPS
        old_board = board.board
        copy_board = deepcopy(board.board)
        for i in strs:
            for x in range(board.count_x):
                copy_board[x][i] = []
        main.game.FPS = 2
        main.game.score += 1
        self.select_figure.render_to_board = lambda: 0
        self.select_figure.down_move = lambda: True

        def a(i):
            if i == 0:
                main.game.FPS = old_FPS
                for o_index in range(len(strs)):
                    o = strs[o_index]
                    for y in range(o, main.game.line_level, -1):
                        for x in range(board.count_x):
                            board.board[x][y] = board.board[x][y - 1]
                            board.board[x][y - 1] = []
                self.create()
                return
            if i % 2:
                board.board = copy_board
            else:
                board.board = old_board
            main.game.scheduler.add_task(lambda: a(i - 1), 1)

        a(1)


class Figure:
    ROTATE_LEFT = -1
    ROTATE_RIGHT = 1

    def __init__(self, schem):
        self.schem = schem
        self.old_render = []
        self.uncompress()
        self.coords = [(self.get_board().count_x - len(self.schem[0])) // 2, 0]
        self.collide_setup()

    def get_board(self):
        return main.game.board

    def collide_setup(self):
        self.down_collide_cells = [0] * len(self.schem[0])
        for column in range(len(self.schem[0])):
            for string in range(len(self.schem)):
                if self.schem[string][column]:
                    self.down_collide_cells[column] = string + 1
        self.right_collide_cells = [0] * len(self.schem)
        for string in range(len(self.schem)):
            for column in range(len(self.schem[0])):
                if self.schem[string][column]:
                    self.right_collide_cells[string] = column + 1
        self.left_collide_cells = [len(self.schem[0]) - 1] * len(self.schem)
        for string in range(len(self.schem)):
            for column in range(len(self.schem[0])):
                if self.schem[string][column]:
                    self.left_collide_cells[string] = column - 1
                    break

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
                                  for _ in range(max_len - len(self.rotate_schem))]

    def rotate(self, ROTATE):
        old_schemas = [deepcopy(self.schem), deepcopy(self.rotate_schem)]
        length = len(self.rotate_schem)
        new_schem = deepcopy(self.rotate_schem)
        for x in range(length):
            for y in range(length):
                if ROTATE == self.ROTATE_RIGHT:
                    new_schem[length - y - 1][x] = self.rotate_schem[x][y]
                else:
                    new_schem[y][length - x - 1] = self.rotate_schem[x][y]
        self.rotate_schem = new_schem
        self.compress()
        if self.coords[0] + len(self.schem[0]) > self.get_board().count_x:
            self.coords[0] = self.get_board().count_x - len(self.schem[0])
        self.clear_rendered()
        for y in range(len(self.schem)):
            old_y = y
            for x in range(len(self.schem[0])):
                y = old_y
                if self.schem[y][x]:
                    x += self.coords[0]
                    y += self.coords[1]
                    if self.get_board().board[x][y]:
                        self.schem, self.rotate_schem = old_schemas
                        return
        self.collide_setup()

    def clear_rendered(self):
        for x, y in self.old_render:
            self.get_board().board[x][y] = []
        self.old_render = []

    def render_to_board(self):
        self.clear_rendered()
        for y in range(len(self.schem)):
            for x in range(len(self.schem[0])):
                x2 = x
                y2 = y
                if self.schem[y][x]:
                    x2 += self.coords[0]
                    y2 += self.coords[1]
                    self.get_board().board[x2][y2] = main.game.figures_handler.color_now
                    self.old_render.append((x2, y2))

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
        if self.check_left_move():
            self.coords[0] -= 1

    def check_down_move(self):
        """проверяется место под фигурой при down_move
        True - если есть место, False - если нет места"""
        if len(self.schem) + self.coords[1] >= self.get_board().count_y:
            return False
        coords_copy = self.coords.copy()
        for y in self.down_collide_cells:
            coords_copy[1] = self.coords[1] + y
            if self.get_board().board[coords_copy[0]][coords_copy[1]]:
                return False
            coords_copy[0] += 1
        return True

    def check_right_move(self):
        """проверяется место справа от фигуры при right_move
        True - если есть место, False - если нет места"""
        if len(self.schem[0]) + self.coords[0] >= self.get_board().count_x:
            return False
        coords_copy = self.coords.copy()
        for x in self.right_collide_cells:
            coords_copy[0] = self.coords[0] + x
            if self.get_board().board[coords_copy[0]][coords_copy[1]]:
                return False
            coords_copy[1] += 1
        return True

    def check_left_move(self):
        """проверяется место слева от  фигуры при left_move
        True - если есть место, False - если нет места"""
        if self.coords[0] == 0:
            return False
        coords_copy = self.coords.copy()
        for x in self.left_collide_cells:
            coords_copy[0] = self.coords[0] + x
            if self.get_board().board[coords_copy[0]][coords_copy[1]]:
                return False
            coords_copy[1] += 1
        return True

    def copy(self):
        return Figure(self.schem)


main = Main()
main.start()

import tkinter as tk  # Importa la biblioteca tkinter para la interfaz gráfica
import random         # Importa la biblioteca random para generar números aleatorios
from threading import Lock  # Importa Lock para asegurar que ciertos procesos no ocurran simultáneamente


# Definición de colores brillantes y vibrantes para las piezas del Tetris
COLORS = ['black', 'cyan', 'magenta', 'yellow', 'green', 'orange', 'red']

# Clase principal que implementa la lógica del juego Tetris
class Tetris():
    FIELD_HEIGHT = 20 # Altura del campo de juego
    FIELD_WIDTH = 10  # Anchura del campo de juego
     # Puntuaciones por líneas eliminadas, donde el índice indica el número de líneas eliminadas
    SCORE_PER_ELIMINATED_LINES = (0, 40, 100, 300, 1200)
    
    # Definición de las diferentes formas de Tetrominos (piezas)
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1, 1)], # O
        [(0, 0), (0, 1), (1, 1), (2, 1)], # L
        [(0, 1), (1, 1), (2, 1), (2, 0)], # J
        [(0, 1), (1, 0), (1, 1), (2, 0)], # Z
        [(0, 1), (1, 0), (1, 1), (2, 1)], # T
        [(0, 0), (1, 0), (1, 1), (2, 1)], # S
        [(0, 1), (1, 1), (2, 1), (3, 1)], # I
    ]
    
    def __init__(self):
        """Inicializa los atributos del juego, como el campo de juego, puntaje y nivel"""
        # Crear el campo de juego vacío (lista de listas)
        self.field = [[0 for c in range(Tetris.FIELD_WIDTH)] for r in range(Tetris.FIELD_HEIGHT)]
        self.score = 0 # Puntaje inicial
        self.level = 0 # Nivel inicial
        self.total_lines_eliminated = 0
        self.game_over = False
        self.move_lock = Lock()
        self.reset_tetromino()

    def reset_tetromino(self):
        self.tetromino = random.choice(Tetris.TETROMINOS)[:]
        self.tetromino_color = random.randint(1, len(COLORS)-1)
        self.tetromino_offset = [-2, Tetris.FIELD_WIDTH // 2]
        self.game_over = any(not self.is_cell_free(r, c) for (r, c) in self.get_tetromino_coords())

    def get_tetromino_coords(self):
        return [(r + self.tetromino_offset[0], c + self.tetromino_offset[1]) for (r, c) in self.tetromino]

    def apply_tetromino(self):
        for (r, c) in self.get_tetromino_coords():
            self.field[r][c] = self.tetromino_color

        new_field = [row for row in self.field if any(tile == 0 for tile in row)]
        lines_eliminated = len(self.field) - len(new_field)
        self.total_lines_eliminated += lines_eliminated
        self.field = [[0] * Tetris.FIELD_WIDTH for x in range(lines_eliminated)] + new_field
        self.score += Tetris.SCORE_PER_ELIMINATED_LINES[lines_eliminated] * (self.level + 1)
        self.level = self.total_lines_eliminated // 10
        self.reset_tetromino()

    def get_color(self, r, c):
        return self.tetromino_color if (r, c) in self.get_tetromino_coords() else self.field[r][c]

    def is_cell_free(self, r, c):
        return r < Tetris.FIELD_HEIGHT and 0 <= c < Tetris.FIELD_WIDTH and (r < 0 or self.field[r][c] == 0)

    def move(self, dr, dc):
        with self.move_lock:
            if self.game_over:
                return
                
            if all(self.is_cell_free(r + dr, c + dc) for (r, c) in self.get_tetromino_coords()):
                self.tetromino_offset = [self.tetromino_offset[0] + dr, self.tetromino_offset[1] + dc]
            elif dr == 1 and dc == 0:
                self.game_over = any(r < 0 for (r, c) in self.get_tetromino_coords())
                if not self.game_over:
                    self.apply_tetromino()

    def rotate(self):
        with self.move_lock:
            if self.game_over:
                self.__init__()
                return

            ys = [r for (r, c) in self.tetromino]
            xs = [c for (r, c) in self.tetromino]
            size = max(max(ys) - min(ys), max(xs) - min(xs))
            rotated_tetromino = [(c, size - r) for (r, c) in self.tetromino]

            wallkick_offset = self.tetromino_offset[:]
            tetromino_coord = [(r + wallkick_offset[0], c + wallkick_offset[1]) for (r, c) in rotated_tetromino]
            min_x = min(c for r, c in tetromino_coord)
            max_x = max(c for r, c in tetromino_coord)
            max_y = max(r for r, c in tetromino_coord)
            wallkick_offset[1] -= min(0, min_x)
            wallkick_offset[1] += min(0, Tetris.FIELD_WIDTH - (1 + max_x))
            wallkick_offset[0] += min(0, Tetris.FIELD_HEIGHT - (1 + max_y))

            tetromino_coord = [(r + wallkick_offset[0], c + wallkick_offset[1]) for (r, c) in rotated_tetromino]
            if all(self.is_cell_free(r, c) for (r, c) in tetromino_coord):
                self.tetromino, self.tetromino_offset = rotated_tetromino, wallkick_offset



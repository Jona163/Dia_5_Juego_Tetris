import tkinter as tk  # Importa la biblioteca tkinter para la interfaz gráfica
import random         # Importa la biblioteca random para generar números aleatorios
from threading import Lock  # Importa Lock para asegurar que ciertos procesos no ocurran simultáneamente

# Definición de colores para las piezas del Tetris
COLORS = ['gray', 'lightgreen', 'pink', 'blue', 'orange', 'purple']

# Clase principal que implementa la lógica del juego Tetris
class Tetris():
    # Tamaño del campo de juego
    FIELD_HEIGHT = 20  # Altura del campo de juego
    FIELD_WIDTH = 10   # Anchura del campo de juego
    # Puntuaciones por líneas eliminadas, donde el índice indica el número de líneas eliminadas
    SCORE_PER_ELIMINATED_LINES = (0, 40, 100, 300, 1200)
    
    # Definición de las diferentes formas de Tetrominos (piezas)
    TETROMINOS = [
        [(0, 0), (0, 1), (1, 0), (1,1)],  # O - cuadrado
        [(0, 0), (0, 1), (1, 1), (2,1)],  # L
        [(0, 1), (1, 1), (2, 1), (2,0)],  # J
        [(0, 1), (1, 0), (1, 1), (2,0)],  # Z
        [(0, 1), (1, 0), (1, 1), (2,1)],  # T
        [(0, 0), (1, 0), (1, 1), (2,1)],  # S
        [(0, 1), (1, 1), (2, 1), (3,1)],  # I - línea
    ]
    
    def __init__(self):
        """Inicializa los atributos del juego, como el campo de juego, puntaje y nivel"""
        # Crear el campo de juego vacío (lista de listas)
        self.field = [[0 for c in range(Tetris.FIELD_WIDTH)] for r in range(Tetris.FIELD_HEIGHT)]
        self.score = 0  # Puntaje inicial
        self.level = 0  # Nivel inicial
        self.total_lines_eliminated = 0  # Líneas eliminadas
        self.game_over = False  # Estado del juego
        self.move_lock = Lock()  # Lock para evitar movimientos simultáneos
        self.reset_tetromino()  # Inicia el primer tetromino

    def reset_tetromino(self):
        """Selecciona un nuevo tetromino de forma aleatoria y lo coloca en la posición inicial"""
        self.tetromino = random.choice(Tetris.TETROMINOS)[:]  # Escoge una pieza aleatoria
        self.tetromino_color = random.randint(1, len(COLORS)-1)  # Asigna un color aleatorio
        self.tetromino_offset = [-2, Tetris.FIELD_WIDTH//2]  # Establece la posición inicial de la pieza
        self.game_over = any(not self.is_cell_free(r, c) for (r, c) in self.get_tetromino_coords())

    def get_tetromino_coords(self):
        """Obtiene las coordenadas actuales del tetromino en el campo"""
        return [(r+self.tetromino_offset[0], c + self.tetromino_offset[1]) for (r, c) in self.tetromino]

    def apply_tetromino(self):
        """Aplica el tetromino actual al campo de juego y verifica si se eliminan líneas"""
        for (r, c) in self.get_tetromino_coords():
            self.field[r][c] = self.tetromino_color  # Marca las posiciones ocupadas por el tetromino

        # Elimina las líneas completas y actualiza el campo de juego
        new_field = [row for row in self.field if any(tile == 0 for tile in row)]
        lines_eliminated = len(self.field) - len(new_field)
        self.total_lines_eliminated += lines_eliminated
        self.field = [[0]*Tetris.FIELD_WIDTH for x in range(lines_eliminated)] + new_field
        self.score += Tetris.SCORE_PER_ELIMINATED_LINES[lines_eliminated] * (self.level + 1)  # Actualiza el puntaje
        self.level = self.total_lines_eliminated // 10  # Aumenta el nivel después de eliminar 10 líneas
        self.reset_tetromino()

    def get_color(self, r, c):
        """Devuelve el color de una celda determinada"""
        return self.tetromino_color if (r, c) in self.get_tetromino_coords() else self.field[r][c]
    
    def is_cell_free(self, r, c):
        """Verifica si una celda está libre para colocar una pieza"""
        return r < Tetris.FIELD_HEIGHT and 0 <= c < Tetris.FIELD_WIDTH and (r < 0 or self.field[r][c] == 0)
    
    def move(self, dr, dc):
        """Mueve el tetromino en la dirección indicada (dr: filas, dc: columnas)"""
        with self.move_lock:
            if self.game_over:
                return
            
            # Verifica si la nueva posición está libre
            if all(self.is_cell_free(r + dr, c + dc) for (r, c) in self.get_tetromino_coords()):
                self.tetromino_offset = [self.tetromino_offset[0] + dr, self.tetromino_offset[1] + dc]
            elif dr == 1 and dc == 0:
                self.game_over = any(r < 0 for (r, c) in self.get_tetromino_coords())  # Game over si toca la parte superior
                if not self.game_over:
                    self.apply_tetromino()  # Aplica la pieza al campo

    def rotate(self):
        """Rota el tetromino 90 grados en el sentido de las agujas del reloj"""
        with self.move_lock:
            if self.game_over:
                self.__init__()
                return

            ys = [r for (r, c) in self.tetromino]
            xs = [c for (r, c) in self.tetromino]
            size = max(max(ys) - min(ys), max(xs) - min(xs))
            rotated_tetromino = [(c, size - r) for (r, c) in self.tetromino]

            # Ajusta el tetromino para que no se salga del campo
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


    

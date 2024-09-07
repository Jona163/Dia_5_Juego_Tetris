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
    

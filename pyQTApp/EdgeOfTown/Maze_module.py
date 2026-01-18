import math

from PyQt5.QtCore import Qt, QPoint, QTimer, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPolygon
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QFrame, QWidget

from pyQTApp.qt_designer_widgets.edgeOfTownWindow import Ui_EdgeOfTownWindow
from pyQTApp.qt_designer_widgets.maze_QFrame import Ui_mazeFrame

# from PyQt6.QtWidgets import QMainWindow, QFrame, QSizePolicy
# from PyQt6.QtCore import Qt, QPoint
# from PyQt6.QtGui import QPainter, QPen, QColor
import random

class Maze_UI(QMainWindow):
    def __init__(self, edge_of_town_window: QMainWindow, edge_of_town_ui: Ui_EdgeOfTownWindow):
        super().__init__()
        # self.ui = Ui_combatWindow()
        # self.ui.setupUi(self)
        self.mazeFrame = QFrame()
        self.ui = Ui_mazeFrame()
        self.ui.setupUi(self.mazeFrame)
        layout = edge_of_town_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.mazeFrame)
        # layout.addWidget(self.tavernFrame, alignment=Qt.AlignmentFlag.AlignRight)
        self.mazeFrame.setGeometry(edge_of_town_ui.mazeFrame.geometry())
        # Make tavernFrame resize with castleFrame
        self.mazeFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.maze_widget = MazeWidget()
        layout.addWidget(self.maze_widget)

        # self.maze_widget = MazeWidget(maze)
        # self.ui.mazeFrame.layout().addWidget(self.maze_widget)

import random

def generate_maze(width, height):
    # Ensure dimensions are odd
    width = width if width % 2 == 1 else width + 1
    height = height if height % 2 == 1 else height + 1

    # Initialize maze with walls (1)
    maze = [[1 for _ in range(width)] for _ in range(height)]

    # Define directions: (dx, dy)
    directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]

    def is_valid(nx, ny):
        return 0 < nx < width and 0 < ny < height

    def carve_passages(cx, cy):
        maze[cy][cx] = 0  # Mark current cell as path
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = cx + dx, cy + dy
            if is_valid(nx, ny) and maze[ny][nx] == 1:
                maze[cy + dy // 2][cx + dx // 2] = 0  # Remove wall between cells
                carve_passages(nx, ny)

    # Start carving from (1, 1)
    carve_passages(1, 1)
    return maze

class MazeWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.maze = generate_maze(10, 10)
        self.maze_height = len(self.maze)
        self.maze_width = len(self.maze[0])
        self.tile_width = 64
        self.tile_height = 32
        self.player_pos = (1, 1)

    def iso_coords(self, x, y):
        """
        Convert grid coordinates (x, y) to isometric screen coordinates (screen_x, screen_y).
        """
        screen_x = (x - y) * (self.tile_width // 2)
        screen_y = (x + y) * (self.tile_height // 2)
        return screen_x, screen_y

    def paintEvent(self, event):
        painter = QPainter(self)
        for y in range(self.maze_height):
            for x in range(self.maze_width):
                tile = self.maze[y][x]
                screen_x, screen_y = self.iso_coords(x, y)
                if tile == 'floor':
                    self.draw_floor(painter, screen_x, screen_y)
                elif tile == 'wall':
                    # Defer drawing walls until after the player
                    continue
            # After drawing floor tiles in the row, check if the player is in this row
            if self.player_pos[1] == y:
                px, py = self.player_pos
                player_screen_x, player_screen_y = self.iso_coords(px, py)
                self.draw_player(painter, player_screen_x, player_screen_y)
            # Now draw wall tiles for this row
            for x in range(self.maze_width):
                tile = self.maze[y][x]
                if tile == 'wall':
                    screen_x, screen_y = self.iso_coords(x, y)
                    self.draw_wall(painter, screen_x, screen_y)

    def draw_player(self, painter, x, y):
        """
        Draws the player character at the specified isometric screen coordinates.
        """
        # Define the size of the player representation
        player_width = self.tile_width // 2
        player_height = self.tile_height

        # Create a rectangle representing the player
        rect = QRect(x, y - player_height // 2, player_width, player_height)

        # Set the brush and pen for drawing
        painter.setBrush(QBrush(QColor(0, 0, 0, 200)))  # Semi-transparent black
        painter.setPen(QPen(Qt.black))

        # Draw the ellipse representing the player
        painter.drawEllipse(rect)

    def draw_tile(self, painter, x, y, color):
        points = [
            QPoint(x, y + self.tile_height // 2),
            QPoint(x + self.tile_width // 2, y),
            QPoint(x + self.tile_width, y + self.tile_height // 2),
            QPoint(x + self.tile_width // 2, y + self.tile_height),
        ]
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.black))
        painter.drawPolygon(QPolygon(points))

    def keyPressEvent(self, event):
        dx, dy = 0, 0
        if event.key() == Qt.Key_Z:
            dy = -1
        elif event.key() == Qt.Key_S:
            dy = 1
        elif event.key() == Qt.Key_Q:
            dx = -1
        elif event.key() == Qt.Key_D:
            dx = 1
        new_x = self.player_pos[0] + dx
        new_y = self.player_pos[1] + dy
        if 0 <= new_y < len(self.maze) and 0 <= new_x < len(self.maze[0]):
            if self.maze[new_y][new_x] == 0:
                self.player_pos = (new_x, new_y)
                self.update()


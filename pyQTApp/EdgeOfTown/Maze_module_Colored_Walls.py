import math

from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QMainWindow, QSizePolicy, QFrame

from pyQTApp.qt_designer_widgets.edgeOfTownWindow import Ui_EdgeOfTownWindow
from pyQTApp.qt_designer_widgets.maze_QFrame import Ui_mazeFrame

# from PyQt6.QtWidgets import QMainWindow, QFrame, QSizePolicy
# from PyQt6.QtCore import Qt, QPoint
# from PyQt6.QtGui import QPainter, QPen, QColor
import random

# class Maze_UI(QMainWindow):
#     def __init__(self, edge_of_town_window: QMainWindow, edge_of_town_ui: Ui_EdgeOfTownWindow):
#         super().__init__()
#         # self.ui = Ui_combatWindow()
#         # self.ui.setupUi(self)
#         self.mazeFrame = QFrame()
#         self.ui = Ui_mazeFrame()
#         self.ui.setupUi(self.mazeFrame)
#         layout = edge_of_town_window.layout()
#         layout.setAlignment(Qt.AlignmentFlag.AlignTop)
#
#         layout.addWidget(self.mazeFrame)
#         # layout.addWidget(self.tavernFrame, alignment=Qt.AlignmentFlag.AlignRight)
#         self.mazeFrame.setGeometry(edge_of_town_ui.mazeFrame.geometry())
#         # Make tavernFrame resize with castleFrame
#         self.mazeFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)


class Maze_UI(QMainWindow):
    def __init__(self, edge_of_town_window: QMainWindow, edge_of_town_ui):
        super().__init__()
        self.mazeFrame = QFrame()
        self.ui = Ui_mazeFrame()
        self.ui.setupUi(self.mazeFrame)

        # Maze configuration
        self.cell_size = 50
        self.maze_width = 10
        self.maze_height = 10
        self.wall_height = 100

        # Player position and orientation
        self.player_x = 1.5
        self.player_y = 1.5
        self.player_angle = 0  # In radians
        self.fov = math.pi / 3  # 60 degrees field of view

        # Initialize maze
        self.maze_data = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 0, 0, 0, 0, 1, 0, 0, 1], [1, 0, 1, 1, 0, 1, 1, 0, 1, 1], [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0, 1, 1, 0, 1], [1, 0, 0, 0, 1, 0, 0, 0, 0, 1], [1, 1, 1, 0, 1, 1, 0, 1, 0, 1], [1, 0, 0, 0, 0, 0, 0, 1, 0, 1], [1, 0, 1, 1, 1, 1, 0, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

        # Set up the frame
        layout = edge_of_town_window.layout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.mazeFrame)
        self.mazeFrame.setGeometry(edge_of_town_ui.mazeFrame.geometry())
        self.mazeFrame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Enable painting and key events
        self.mazeFrame.paintEvent = self.paintEvent
        self.mazeFrame.keyPressEvent = self.keyPressEvent
        self.mazeFrame.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Set up animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.mazeFrame.update)
        self.timer.start(16)  # ~60 FPS

    def ray_cast(self, angle):
        # Ray casting algorithm
        x, y = self.player_x, self.player_y
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)

        # Distance to wall
        distance = 0
        while True:
            distance += 0.1
            test_x = x + cos_a * distance
            test_y = y + sin_a * distance

            # Check if ray hit a wall
            map_x = int(test_x)
            map_y = int(test_y)

            if map_x < 0 or map_x >= self.maze_width or map_y < 0 or map_y >= self.maze_height:
                break

            if self.maze_data[map_y][map_x] == 1:
                return distance

        return float('inf')

    def paintEvent(self, event):
        if not hasattr(self.mazeFrame, 'width'):
            return

        painter = QPainter(self.mazeFrame)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Clear background
        painter.fillRect(0, 0, self.mazeFrame.width(), self.mazeFrame.height(), QColor(0, 0, 0))

        # Draw 3D view
        num_rays = self.mazeFrame.width() // 2
        for x in range(num_rays):
            # Calculate ray angle
            ray_angle = self.player_angle - self.fov / 2 + (x / num_rays) * self.fov

            # Get distance to wall
            distance = self.ray_cast(ray_angle)

            # Calculate wall height
            if distance < 0.1:
                distance = 0.1
            wall_height = min(int(self.wall_height / distance), self.mazeFrame.height())

            # Calculate wall position
            wall_top = self.mazeFrame.height() // 2 - wall_height // 2
            wall_bottom = wall_top + wall_height

            # Draw wall slice
            intensity = min(1.0, 1.0 / (distance * 0.3))
            color = QColor(0, 100, 255)
            color.setAlphaF(intensity * 0.7)  # Filigree effect

            painter.setPen(QPen(color, 2))
            painter.drawLine(x * 2, wall_top, x * 2, wall_bottom)

        painter.end()

    def keyPressEvent(self, event):
        # Movement speed
        move_speed = 0.1
        rotation_speed = 0.1

        # Handle movement
        if event.key() == Qt.Key.Key_W:
            new_x = self.player_x + math.cos(self.player_angle) * move_speed
            new_y = self.player_y + math.sin(self.player_angle) * move_speed
            if self.maze_data[int(new_y)][int(new_x)] == 0:
                self.player_x, self.player_y = new_x, new_y

        elif event.key() == Qt.Key.Key_S:
            new_x = self.player_x - math.cos(self.player_angle) * move_speed
            new_y = self.player_y - math.sin(self.player_angle) * move_speed
            if self.maze_data[int(new_y)][int(new_x)] == 0:
                self.player_x, self.player_y = new_x, new_y

        elif event.key() == Qt.Key.Key_A:
            self.player_angle -= rotation_speed

        elif event.key() == Qt.Key.Key_D:
            self.player_angle += rotation_speed

        self.mazeFrame.update()

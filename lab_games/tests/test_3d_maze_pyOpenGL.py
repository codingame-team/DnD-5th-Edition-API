import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def create_maze(width, height):
    maze = np.ones((width, height))
    maze[1:-1, 1:-1] = 0
    maze[1, 1] = 1
    maze[width-2, height-2] = 1
    return maze

def draw_cube(position):
    x, y, z = position
    vertices = [
        (x, y, z), (x+1, y, z), (x+1, y+1, z), (x, y+1, z),
        (x, y, z+1), (x+1, y, z+1), (x+1, y+1, z+1), (x, y+1, z+1)
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]

    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def display_maze(maze):
    width, height = maze.shape
    for x in range(width):
        for y in range(height):
            if maze[x, y] == 1:
                draw_cube((x, y, 0))

def main():
    width, height = 10, 10
    maze = create_maze(width, height)

    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    gluPerspective(45, (display[0] / display[1]), 0.1, 50.0)
    glTranslatef(-width//2, -height//2, -20)

    glEnable(GL_DEPTH_TEST)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        glRotatef(1, 3, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        display_maze(maze)
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection, Line3DCollection

def create_maze(width, height):
    maze = np.ones((width, height))
    maze[1:-1, 1:-1] = 0
    maze[1, 1] = 1
    maze[width-2, height-2] = 1
    return maze

def plot_maze_3d(maze):
    width, height = maze.shape
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot walls
    for x in range(width):
        for y in range(height):
            if maze[x, y] == 1:
                z = 0
                vertices = [
                    [(x, y, z), (x+1, y, z), (x+1, y+1, z), (x, y+1, z)],  # Bottom face
                    [(x, y, z+1), (x+1, y, z+1), (x+1, y+1, z+1), (x, y+1, z+1)],  # Top face
                    [(x, y, z), (x, y, z+1), (x, y+1, z+1), (x, y+1, z)],  # Front face
                    [(x+1, y, z), (x+1, y, z+1), (x+1, y+1, z+1), (x+1, y+1, z)],  # Back face
                    [(x, y, z), (x, y, z+1), (x+1, y, z+1), (x+1, y, z)],  # Left face
                    [(x, y+1, z), (x, y+1, z+1), (x+1, y+1, z+1), (x+1, y+1, z)]  # Right face
                ]
                ax.add_collection3d(Poly3DCollection(vertices, edgecolor='k', linewidths=1, alpha=0.25))

    # Set the aspect ratio
    ax.set_aspect('auto')

    # Set limits
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_zlim(0, 2)

    # Set labels
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()

# Create a simple maze
width, height = 10, 10
maze = create_maze(width, height)

# Plot the maze in 3D
plot_maze_3d(maze)

import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Data Display Table")

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Define your data (example)
data = [
    ["Name", "Score"],
    ["Alice", "95"],
    ["Bob", "87"],
    ["Charlie", "92"],
    ["David", "88"]
]

# Define font
font = pygame.font.SysFont(None, 24)

# Function to draw the table
def draw_table(data):
    cell_width = SCREEN_WIDTH // len(data[0])
    cell_height = 30
    x = 50
    y = 50

    # Draw headers
    for i, header in enumerate(data[0]):
        cell_rect = pygame.Rect(x + i * cell_width, y, cell_width, cell_height)
        pygame.draw.rect(screen, GRAY, cell_rect, 1)
        draw_text(header, font, BLACK, screen, x + i * cell_width + cell_width // 2, y + cell_height // 2)

    # Draw data rows
    for row_index, row in enumerate(data[1:], start=1):
        for col_index, cell in enumerate(row):
            cell_rect = pygame.Rect(x + col_index * cell_width, y + row_index * cell_height, cell_width, cell_height)
            pygame.draw.rect(screen, WHITE, cell_rect)
            pygame.draw.rect(screen, GRAY, cell_rect, 1)
            draw_text(cell, font, BLACK, screen, x + col_index * cell_width + cell_width // 2,
                      y + row_index * cell_height + cell_height // 2)

# Function to draw text
def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(str(text), True, color)
    text_rect = text_obj.get_rect()
    text_rect.center = (x, y)
    surface.blit(text_obj, text_rect)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(WHITE)

    # Draw the table
    draw_table(data)

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()

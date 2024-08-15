import random

import pygame

# Define the colors and their RGB values
COLORS = ['R', 'G', 'B', 'Y', 'O', 'P']
COLOR_MAP = {
    'R': (255, 0, 0),  # Red
    'G': (0, 255, 0),  # Green
    'B': (0, 0, 255),  # Blue
    'Y': (255, 255, 0),  # Yellow
    'O': (255, 165, 0),  # Orange
    'P': (128, 0, 128)  # Purple
}


def get_secret_code(num_colors):
    """
    Returns a list of randomly selected colors of given length
    """
    return random.sample(COLORS, num_colors)


def get_num_correct_colors(guess, secret_code):
    """
    Returns the number of correct colors in the guess
    """
    return sum(min(guess.count(c), secret_code.count(c)) for c in set(COLORS))


def get_num_correct_positions(guess, secret_code):
    """
    Returns the number of colors in the correct position
    """
    return sum(g == s for g, s in zip(guess, secret_code))


def play_game_pygame():
    # Initialize Pygame
    pygame.init()

    # Set up the window
    WINDOW_WIDTH = 900
    WINDOW_HEIGHT = 600
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Mastermind")

    # Define colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

    # Set up the game
    num_colors = 4
    secret_code = get_secret_code(num_colors)
    print(f"hidden code: {''.join(secret_code)}")
    guess = []

    # Set up font for displaying text
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 24)
    large_font = pygame.font.SysFont('Arial', 30)

    # List to store past guesses and their feedback
    past_guesses = []

    # Flag to indicate if the game is won
    game_won = False

    # Scrolling parameters
    scroll_offset = 0
    max_visible_guesses = (WINDOW_HEIGHT - 200) // 50  # Number of guesses that fit on the screen

    # Game loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Ask the user if they want to quit or restart
                    quit_or_restart = pygame.Surface((400, 200))
                    quit_or_restart.fill((255, 255, 255))
                    quit_or_restart_rect = quit_or_restart.get_rect()
                    quit_or_restart_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
                    quit_text = pygame.font.Font(None, 36).render("Press Q to Quit or R to Restart", True, (0, 0, 0))
                    quit_text_rect = quit_text.get_rect()
                    quit_text_rect.center = quit_or_restart_rect.center
                    window.blit(quit_or_restart, quit_or_restart_rect)
                    window.blit(quit_text, quit_text_rect)
                    pygame.display.flip()

                    while True:
                        event = pygame.event.wait()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                running = False
                                break
                            elif event.key == pygame.K_r:
                                # Restart the game
                                secret_code = get_secret_code(num_colors)
                                guess = []
                                past_guesses = []
                                game_won = False
                                break
                elif not game_won:
                    if event.key == pygame.K_RETURN:
                        # Check the guess
                        if len(guess) == num_colors:
                            num_correct_positions = get_num_correct_positions(guess, secret_code)
                            num_correct_colors = get_num_correct_colors(guess, secret_code)

                            # Store the current guess and feedback
                            feedback = f"{num_correct_positions} correct positions, {num_correct_colors - num_correct_positions} correct colors"
                            past_guesses.append((list(guess), feedback))

                            # Check if the game is won
                            if num_correct_positions == num_colors:
                                feedback = f"Congratulations! You guessed the code in {len(past_guesses)} attempts!"
                                game_won = True

                            guess = []

                            # Adjust scroll to always show the last guess
                            if len(past_guesses) > max_visible_guesses:
                                scroll_offset = len(past_guesses) - max_visible_guesses
                    elif event.key == pygame.K_BACKSPACE:
                        if guess:
                            guess.pop()
                    else:
                        key_to_color = {
                            pygame.K_r: 'R',
                            pygame.K_g: 'G',
                            pygame.K_b: 'B',
                            pygame.K_y: 'Y',
                            pygame.K_o: 'O',
                            pygame.K_p: 'P'
                        }
                        if event.key in key_to_color:
                            guess.append(key_to_color[event.key])
                            if len(guess) > num_colors:
                                guess = guess[-num_colors:]

        # Clear the window
        window.fill(WHITE)

        # Draw past guesses and their feedback with scrolling
        y_start = 100
        visible_guesses = past_guesses[scroll_offset:scroll_offset + max_visible_guesses]
        for guess_entry, feedback in visible_guesses:
            x = 50
            for color in guess_entry:
                pygame.draw.circle(window, COLOR_MAP[color], (x, y_start), 20)
                x += 50
            feedback_text = font.render(feedback, True, BLACK)
            window.blit(feedback_text, (x + 20, y_start - 10))
            y_start += 50

        # Draw the current guess if the game is not won
        if not game_won:
            x = 50
            for color in guess:
                pygame.draw.circle(window, COLOR_MAP[color], (x, y_start), 20)
                x += 50
        else:
            # Display "Congratulations!" message after the last guess
            if len(past_guesses) > max_visible_guesses:
                y_start = 100 + (len(visible_guesses) - 1) * 50
            feedback = f"Congratulations! You guessed the code in {len(past_guesses)} attempts!"
            congrat_text = large_font.render(feedback, True, BLACK)
            window.blit(congrat_text, (50, y_start + 50))

        # Update the display
        pygame.display.update()

    # Quit Pygame
    pygame.quit()


if __name__ == "__main__":
    play_game_pygame()

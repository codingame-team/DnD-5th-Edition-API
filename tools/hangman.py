import os
import sys

import pygame
import random


def resource_path(relative_path):
	""" Get the absolute path to a resource, works for dev and for PyInstaller """
	if hasattr(sys, '_MEIPASS'):
		return os.path.join(sys._MEIPASS, relative_path)
	return os.path.join(os.path.abspath("."), relative_path)


# Initialisation de Pygame
pygame.init()

# Constantes
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FONT = pygame.font.SysFont('arial', 40)
LETTERS_FONT = pygame.font.SysFont('arial', 60)
WORD_FONT = pygame.font.SysFont('arial', 80)

# Configuration de l'écran
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jeu de Pendu")

# Chargement des images du pendu
images = []
for i in range(7):
	image = pygame.image.load(resource_path(f"data/hangman{i}.png"))
	images.append(image)

# Mots pour le jeu
words = ["PYTHON", "DEVELOPPEUR", "PENDU", "PROGRAMMATION", "ALGORITHME"]
word = random.choice(words)
guessed = ["_"] * len(word)

# Variables de jeu
hangman_status = 0
guessed_letters = []
game_over = False


# Dessiner le mot à deviner
def draw_word():
	display_word = " ".join(guessed)
	text = WORD_FONT.render(display_word, True, BLACK)
	screen.blit(text, (400 - text.get_width() // 2, 200))


# Dessiner les lettres déjà devinées
def draw_letters():
	for i, letter in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
		x = 20 + (i % 13) * 50
		y = 400 + (i // 13) * 60
		text = LETTERS_FONT.render(letter, True, BLACK)
		screen.blit(text, (x, y))
		if letter in guessed_letters:
			pygame.draw.line(screen, BLACK, (x, y + 50), (x + 40, y + 50), 5)


# Vérifier si le jeu est gagné
def check_win():
	return "_" not in guessed


# Boucle principale du jeu
running = True
while running:
	screen.fill(WHITE)

	# Affichage du pendu
	screen.blit(images[hangman_status], (150, 100))

	# Affichage du mot et des lettres
	draw_word()
	draw_letters()

	pygame.display.update()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN and not game_over:
			letter = event.unicode.upper()
			if letter.isalpha() and letter not in guessed_letters:
				guessed_letters.append(letter)
				if letter in word:
					for i, char in enumerate(word):
						if char == letter:
							guessed[i] = letter
					if check_win():
						game_over = True
				else:
					hangman_status += 1
					if hangman_status == 6:
						game_over = True

	if game_over:
		if check_win():
			draw_letters()
			message = "GAGNÉ !"
		else:
			message = "PERDU ! Le mot était : " + word
		text = FONT.render(message, True, BLACK)
		screen.blit(text, (400 - text.get_width() // 2, 350))
		pygame.display.update()
		pygame.time.wait(5000)
		running = False
		input('press a key to continue...')

pygame.quit()

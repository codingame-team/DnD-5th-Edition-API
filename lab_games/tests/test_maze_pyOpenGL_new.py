import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image
import numpy as np


def charger_texture(fichier):
    # Charger l'image
    img = Image.open(fichier)
    # Redimensionner l'image à 100x100 pixels
    resized_img = img.resize((100, 100))
    # Convertir l'image en mode RGB si elle ne l'est pas déjà
    resized_img = resized_img.convert('RGB')
    # Convertir les données d'image en tableau numpy (de type uint8)
    img_data = np.array(resized_img, dtype=np.uint8)
    # Générer une texture ID
    texture_id = glGenTextures(1)
    # Lier la texture
    glBindTexture(GL_TEXTURE_2D, texture_id)
    # Définir les paramètres de texture
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    # Charger les données de texture
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, resized_img.size[0], resized_img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture_id


def init_opengl(width, height):
    # Initialiser Pygame et le contexte OpenGL
    pygame.init()
    pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, (width / height), 0.1, 50.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def draw_scene(texture_id):
    # Effacer l'écran
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Déplacer la scène en arrière
    glTranslatef(0.0, 0.0, -5)

    # Activer la texture
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glEnable(GL_TEXTURE_2D)

    # Dessiner un carré avec la texture appliquée
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0);
    glVertex3f(-1, -1, 0)
    glTexCoord2f(1, 0);
    glVertex3f(1, -1, 0)
    glTexCoord2f(1, 1);
    glVertex3f(1, 1, 0)
    glTexCoord2f(0, 1);
    glVertex3f(-1, 1, 0)
    glEnd()

    # Désactiver la texture
    glDisable(GL_TEXTURE_2D)

    # Mettre à jour l'affichage
    pygame.display.flip()


def main():
    # Initialiser OpenGL
    init_opengl(800, 600)

    # Chemin complet du fichier image
    fichier = 'textures/b&w_texture.jpg'

    # Charger la texture
    texture_id = charger_texture(fichier)

    # Boucle principale
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        # Dessiner la scène
        draw_scene(texture_id)

    pygame.quit()


if __name__ == '__main__':
    main()

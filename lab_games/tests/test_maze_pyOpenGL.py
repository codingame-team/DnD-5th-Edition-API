import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# import PIL.Image as Image
from PIL import Image

import numpy

# Paramètres de la fenêtre
largeur_fenetre = 800
hauteur_fenetre = 600

# Initialisation de la position du joueur
position_joueur = [0, 0, -5]

# Initialisation de la direction du regard du joueur
regard_joueur = [0, 0, -1]

def initialiser():
    glClearColor(0.0, 0.0, 0.0, 1.0) # Couleur de fond
    glEnable(GL_DEPTH_TEST) # Active le test de profondeur

def dessiner():
    global position_joueur, regard_joueur

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Position et orientation de la caméra (vue subjective)
    gluLookAt(
        position_joueur[0], position_joueur[1], position_joueur[2],
        position_joueur[0] + regard_joueur[0], position_joueur[1] + regard_joueur[1], position_joueur[2] + regard_joueur[2],
        0, 1, 0
    )

    # Dessiner le labyrinthe ici

    glutSwapBuffers()

def mise_a_jour(val):
    # Mettre à jour la position du joueur ici

    glutPostRedisplay()
    glutTimerFunc(16, mise_a_jour, 0)

def touches_presseees(*args):
    # Gérer les entrées clavier pour le déplacement du joueur

    glutPostRedisplay()


# Charger l'image de texture
def charger_texture(fichier):
    img = Image.open(fichier)
    resized_img = img.resize((100, 100))  # Redimensionne l'image à 100x100 pixels
    resized_img = resized_img.convert('RGB')
    img_data = np.array(resized_img, dtype=np.uint8)
    # img_data = np.array(list(resized_img.getdata()), np.int8)
    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
    return texture_id

# Appliquer la texture à un quadrilatère
def appliquer_texture(texture_id):
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex3f(-1.0, -1.0,  0.0)
    glTexCoord2f(1.0, 0.0); glVertex3f( 1.0, -1.0,  0.0)
    glTexCoord2f(1.0, 1.0); glVertex3f( 1.0,  1.0,  0.0)
    glTexCoord2f(0.0, 1.0); glVertex3f(-1.0,  1.0,  0.0)
    glEnd()
    glDisable(GL_TEXTURE_2D)



if __name__ == "__main__":
    # Utilisation dans le programme principal
    # img = Image.open('textures/b&w_texture.jpg')
    # resized_img = img.resize((100, 100))  # Redimensionne l'image à 100x100 pixels
    # resized_img.show()
    # exit()
    texture_id = charger_texture('textures/b&w_texture.jpg')
    appliquer_texture(texture_id)

    glutInit()
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(largeur_fenetre, hauteur_fenetre)
    glutCreateWindow("Labyrinthe 3D")

    initialiser()

    glutDisplayFunc(dessiner)
    glutTimerFunc(0, mise_a_jour, 0)
    glutKeyboardFunc(touches_presseees)

    glutMainLoop()

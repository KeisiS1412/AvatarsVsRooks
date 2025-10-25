import pygame
from Scene import Scene
from Matrix import Matrix

class GameScene(Scene):
    """Escena de registro con campos de texto, menús desplegables y botones."""
    def __init__(self, font, res, switchSceneCallback):  # Inicializa la escena
        self.switchScene = switchSceneCallback
        self.res = res
        self.matrix = Matrix(self.res)

    def draw(self, screen): #Dibuja todos los elementos en pantalla
        self.matrix.draw(screen)

    def handleEvent(self, event): #Detección de donde se hace click y llama a las fucniones que correspondan
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.matrix.deteckClick()



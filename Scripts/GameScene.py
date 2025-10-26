import pygame
from Scene import Scene
from Matrix import Matrix

class GameScene(Scene):
    """Escena de registro con campos de texto, menús desplegables y botones."""
    def __init__(self, font, res, switchSceneCallback):  # Inicializa la escena
        self.switchScene = switchSceneCallback
        self.res = res
        self.matrix = Matrix(self.res)
        self.coins = 0
        self.selectedRook = None

    def draw(self, screen): #Dibuja todos los elementos en pantalla
        self.matrix.draw(screen)
        self.matrix.drawCoins(screen)

    def handleEvent(self, event): #Detección de donde se hace click y llama a las fucniones que correspondan
        #En el caso de la matriz, si hay un rook seleccionado, lo añade si cumple las condiciones
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.matrix.rect.collidepoint(event.pos):
                if self.selectedRook:
                    if self.selectedRook.cost < self.coins:
                        self.coins  = self.coins - self.selectedRook.cost
                        self.matrix.addRook(event, self.selectedRook)
                else:
                    earned = self.matrix.detectCoinClick(event)
                    self.coins += earned
                    if earned > 0:
                        print(f"Coins: {self.coins}")

    def update(self, dt): #Actualiza la logica de la escena
        self.matrix.update(dt)




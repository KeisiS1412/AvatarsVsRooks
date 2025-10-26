import pygame
from Coins import Coin

class Matrix:
    """Manejo visual y logico de la matriz de juego, maneja instancias de Avatars, Rooks
    monedas, etc. """
class Matrix:
    def __init__(self, res):
        self.ROWS = 9
        self.COLUMNS = 5
        self.createMatrix()
        self.rooksList = []
        self.avatarsList = []
        self.res = res
        self.matrixImage = pygame.transform.rotate(pygame.image.load("Assets/matrix.png"), -90)
        self.matrixImage = pygame.transform.rotozoom(self.matrixImage, 0, 0.61)
        self.cellSize = (self.matrixImage.get_width()//7, self.matrixImage.get_height()//11)
        self.imagePos = (self.res[0]//2 - self.matrixImage.get_width()//2, 0)
        self.rect = pygame.Rect(
            self.imagePos[0] + self.cellSize[0],
            self.imagePos[1] + self.cellSize[1],
            self.matrixImage.get_width() - 2 * self.cellSize[0],
            self.matrixImage.get_height() - 2 * self.cellSize[1]
        )
        coin = Coin()
        self.coins = [coin]

    def createMatrix(self): #Crea una amtriz con listas anidadas del tamño ya establecido
        self.matrix = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw(self, screen): #Dibja primero la matriz, luego los avatars, monedas y rooks.
        screen.blit(self.matrixImage, self.imagePos)

    def addAvatar(self, instance, pos): #Añade un avatar en la posicion dada
        self.matrix[pos[0]][pos[1]] = instance
        self.avatarsList.append(instance)
    
    def addRook(self, event, instance): #Si se clickea una casilla dentro de la matriz, añade el rook en esa posicion
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            pos = self.calculateCell((x,y))
            self.matrix[pos[0]][pos[1]] = instance
            self.rooksList.append(instance)

    def calculateCell(self, clickPos): #Va a calcular en que casilla quedo, ocupo usar modulo, hacer las monedas, colocar cosas y logica de cuando colocar
        rel_x = clickPos[0] - self.rect.x
        rel_y = clickPos[1] - self.rect.y
        col = rel_x // self.cellSize[0]
        row = rel_y // self.cellSize[1]
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            return (row, col)
        else:
            return None
        
    def updateAvatars(self): #Actualiza todos los avatars en la matriz, faltan las clases para completar esta parte
        for avatar in self.avatarsList:
            avatar.update()
    
    def updateRooks(self): #Actualiza todos los rooks en la matriz, faltan las clases para completar esta parte
        for rook in self.rooksList:
            rook.update()

    def updateCoins(self, dt):
        for coin in self.coins:
            coin.update(dt)
    
    def drawCoins(self, screen):
        for coin in self.coins:
            coin.draw(screen, coin.position)

    def update(self, dt): #Actualiza la logica de la matriz
        self.updateCoins(dt)



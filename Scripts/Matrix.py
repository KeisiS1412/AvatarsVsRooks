import pygame

class Matrix:
    """Manejo visual y logico de la matriz de juego, maneja instancias de Avatars, Rooks
    monedas, etc. """
    def __init__(self, res): #Iniciar variables y crear matriz
        self.ROWS = 9
        self.COLUMNS = 5
        self.createMatrix()
        self.rooksList = []
        self.avatarsList = []
        self.res = res
        self.matrixImage = pygame.transform.rotate(pygame.image.load("Assets/matrix.png"), -90)
        self.matrixImage = pygame.transform.rotozoom(self.matrixImage, 0, 0.61)
        self.cellSize = (self.matrixImage.get_width()//7,self.matrixImage.get_height()//11)
        self.rect = pygame.Rect(self.res[0]//2 - self.matrixImage.get_width()//2 + self.cellSize[0], self.cellSize[1], self.matrixImage.get_width() - 2 * self.cellSize[0], self.matrixImage.get_height() - 2 * self.cellSize[1])
        

    def createMatrix(self): #Crea una amtriz con listas anidadas del tamño ya establecido
        self.matriz = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw(self, screen): #Dibja primero la matriz, luego los avatars, monedas y rooks.
        screen.blit(self.matrixImage, (self.rect.topleft))

    def AddAvatar(instance):
        pass
    
    def AddRook(instance):
        pass

    def deteckClick(self, event): #Detecta en que posicion se hizo click, si fue en la imagen
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            pass

    def calculateCell(self, pos): #Va a calcular en que casilla quedo
        pass



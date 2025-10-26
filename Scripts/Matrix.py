import pygame

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

    def createMatrix(self): #Crea una amtriz con listas anidadas del tamño ya establecido
        self.matrix = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw(self, screen): #Dibja primero la matriz, luego los avatars, monedas y rooks.
        screen.blit(self.matrixImage, self.imagePos)

    def addAvatar(instance):
        pass
    
    def addRook(self, event, instance): #Si se clickea una casilla 
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            pos = self.calculateCell((x,y))
            self.matrix[pos[0]][pos[1]] = instance


    def calculateCell(self, clickPos): #Va a calcular en que casilla quedo, ocupo usar modulo, hacer las monedas, colocar cosas y logica de cuando colocar
        rel_x = clickPos[0] - self.rect.x
        rel_y = clickPos[1] - self.rect.y
        col = rel_x // self.cellSize[0]
        row = rel_y // self.cellSize[1]
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            return (row, col)
        else:
            return None



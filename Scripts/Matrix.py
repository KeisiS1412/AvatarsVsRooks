import pygame
from Coins import Coin
import random
from projectiles.FireBall import Fireball
from towers.FireTower import FireTower

class Matrix:
    """Manejo visual y lógico de la matriz de juego, maneja instancias de Avatars, Rooks, monedas y torres."""
    def __init__(self, res):
        self.ROWS = 10
        self.COLUMNS = 6
        self.createMatrix()
        self.rooksList = []
        self.avatarsList = []
        self.res = res
        self.projectiles = []

        self.matrixImage = pygame.transform.rotate(pygame.image.load("Assets/matrix.png"), -90)
        self.matrixImage = pygame.transform.rotozoom(self.matrixImage, 0, 0.61)
        self.cellSize = (self.matrixImage.get_width() // 7, self.matrixImage.get_height() // 11)
        self.imagePos = (self.res[0] // 2 - self.matrixImage.get_width() // 2, 0)

        self.coinCells = set()
        self.rect = pygame.Rect(
            self.imagePos[0],
            self.imagePos[1],
            self.matrixImage.get_width(),
            self.matrixImage.get_height()
        )

        # ► NUEVO: almacenamiento de torres colocadas
        self.towers = {}  # (row, col) -> instancia de Tower

        self.coins = []
        for i in range(5):
            self.addCoin(25)
            self.addCoin(50)
            self.addCoin(100)

    def createMatrix(self):  # Crea una matriz con listas anidadas del tamaño ya establecido
        self.matrix = [[0 for _ in range(self.COLUMNS)] for _ in range(self.ROWS)]

    def draw(self, screen):  # Dibuja primero la matriz, luego torres; las monedas se dibujan aparte
        screen.blit(self.matrixImage, self.imagePos)

        # ► NUEVO: dibuja las torres encima del tablero
        for tower in self.towers.values():
            tower.draw(screen)

        for p in self.projectiles:
            p.draw(screen)

    def _spawn_fireball_below(self, tower):
        row_below = tower.row + 1
        if row_below >= self.ROWS:
            return  # no hay espacio
        tl = self.cell_to_pixel(row_below, tower.col)
        fb = Fireball(self.cellSize)
        x_center = tl[0] + self.cellSize[0] // 2
        y_top = tl[1]
        fb.set_top_center(x_center, y_top)
        self.projectiles.append(fb)

    # ► NUEVO: helper para obtener el topleft en píxeles de una celda
    def cell_to_pixel(self, row, col):
        px = self.imagePos[0] + col * self.cellSize[0]
        py = self.imagePos[1] + row * self.cellSize[1]
        return (px, py)

    def addAvatar(self, instance, pos):  # Añade un avatar en la posición dada
        self.matrix[pos[0]][pos[1]] = instance
        self.avatarsList.append(instance)
    
    def addRook(self, event, instance):  # Si se clickea una casilla dentro de la matriz, añade el rook en esa posición
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            pos = self.calculateCell((x, y))
            if pos is not None and 1 <= pos[0] <= 5 and 1 <= pos[1] <= 9 and self.matrix[pos[0]][pos[1]] == 0:
                self.matrix[pos[0]][pos[1]] = instance
                self.rooksList.append(instance)
                print(f"Rook added at {pos}")

    def calculateCell(self, clickPos):  # Calcula en qué casilla cayó el clic
        x = clickPos[0] - self.rect.x
        y = clickPos[1] - self.rect.y
        col = x // self.cellSize[0]
        row = y // self.cellSize[1]
        if 0 <= row < self.ROWS and 0 <= col < self.COLUMNS:
            return (row, col)
        else:
            return None
        
    def updateAvatars(self):  # Actualiza todos los avatars en la matriz
        for avatar in self.avatarsList:
            avatar.update()
    
    def updateRooks(self):  # Actualiza todos los rooks en la matriz
        for rook in self.rooksList:
            rook.update()

    def updateCoins(self, dt):
        for coin in self.coins:
            coin.update(dt)
    
    def drawCoins(self, screen):
        for coin in self.coins:
            coin.draw(screen, coin.position)

    def update(self, dt):  # Actualiza la lógica de la matriz
        self.updateCoins(dt)
         
        for tower in self.towers.values():
            tower.update(dt)
        
        if hasattr(self, "towers"):
            for tower in self.towers.values():
                tower.update(dt)

                # disparo solo para torres de fuego
                if isinstance(tower, FireTower):
                    if tower.tick_shoot(dt):
                        self._spawn_fireball_below(tower)

        # actualizar proyectiles y limpiar los que salen
        if self.projectiles:
            bottom_y = self.imagePos[1] + self.cellSize[1] * self.ROWS
            alive = []
            for p in self.projectiles:
                p.update(dt)
                if p.rect.top < bottom_y:
                    alive.append(p)   # sigue en juego
                # si ya cruzó el fondo, desapare

    def detectCoinClick(self, event):
        for coin in self.coins:
            if coin.detectClick(event):
                self.coins.remove(coin)
                return coin.value
        return 0
    
    def addCoin(self, val):
        while True:
            x = random.randint(1, self.COLUMNS - 1)
            y = random.randint(1, self.ROWS - 1)
            if (x, y) not in self.coinCells:
                self.coinCells.add((x, y))
                break
        pos = (
            self.imagePos[0] + x * self.cellSize[0] + random.randint(0, 1) * self.cellSize[0] // 2,
            self.imagePos[1] + y * self.cellSize[1] + random.randint(0, 1) * self.cellSize[1] // 2
        )
        newCoin = Coin(val, pos)
        self.coins.append(newCoin)

    # ► NUEVO: reglas para colocar torres
    def can_place_tower(self, row, col):
        # No permitir en última fila ni sobre otra entidad/torre
        if row == self.ROWS - 1:
            return False
        if (row, col) in self.towers:
            return False
        if self.matrix[row][col] != 0:
            return False
        return True

    # ► NUEVO: registrar torre creada por la factory
    def add_tower_instance(self, row, col, tower):
        self.towers[(row, col)] = tower
        self.matrix[row][col] = tower  # opcional, marca ocupación en la lógica

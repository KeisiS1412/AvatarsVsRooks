import pygame

class Selector:
    def __init__(self, cellSize, xlimits, ylimits):
        self.image = pygame.image.load("Assets/selection.png").convert_alpha()
        self.size = cellSize
        self.image = pygame.transform.scale(self.image, self.size)

        self.horizontalLimits = xlimits 
        self.verticalLimits = ylimits 
        self.position = [
            (xlimits[0] + xlimits[1]) // 2,
            (ylimits[0] + ylimits[1]) // 2
        ]

    def moveX(self, direction):
        new_x = self.position[0] + self.size[0] * direction
        if self.horizontalLimits[0] <= new_x <= self.horizontalLimits[1]:
            self.position[0] = new_x

    def moveY(self, direction):
        new_y = self.position[1] + self.size[1] * -direction
        if self.verticalLimits[0] <= new_y <= self.verticalLimits[1]:
            self.position[1] = new_y

    def draw(self, screen):
        screen.blit(self.image, self.position)
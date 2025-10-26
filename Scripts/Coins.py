import pygame

class Coin:
    def __init__(self):
        value = 25
        self.spritesheet = pygame.image.load("Assets/coinsSpritesheet.png").convert_alpha()
        self.SPRITE_WIDTH = 16
        self.SPRITE_HEIGHT = 16
        self.row = 1
        self.sprites = self.getSprites()
        self.currentTime = 0
        self.frameTime = 100
        self.currentFrame = 0
        self.position = (500,500)

    def getSprite(self, x, y):
        """Extrae un sprite en la posición columna x, fila y"""
        rect = pygame.Rect(
            x * self.SPRITE_WIDTH,
            y * self.SPRITE_HEIGHT,
            self.SPRITE_WIDTH,
            self.SPRITE_HEIGHT
        )
        sprite = pygame.Surface((self.SPRITE_WIDTH, self.SPRITE_HEIGHT), pygame.SRCALPHA)
        sprite.blit(self.spritesheet, (0, 0), rect)
        sprite = pygame.transform.scale(sprite, (self.SPRITE_WIDTH * 3, self.SPRITE_HEIGHT * 3))
        return sprite
    
    def getSprites(self):
        sprites = []
        for i in range(4,10):
            sprite = self.getSprite(i, self.row)
            sprites.append(sprite)
        return sprites
    
    def update(self, dt):
        self.currentTime += dt
        if self.currentTime >= self.frameTime:
            self.currentTime = 0
            self.currentFrame = (self.currentFrame + 1) % len(self.sprites)

    def draw(self, screen, pos):
        screen.blit(self.sprites[self.currentFrame], pos)
    

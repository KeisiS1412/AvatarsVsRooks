import pygame

class Coin:
    SPRITE_WIDTH = 16
    SPRITE_HEIGHT = 16
    def __init__(self, val, pos):
        self.value = val
        self.spritesheet = pygame.image.load("Assets/coinsSpritesheet.png").convert_alpha()
        row = {25: 1, 50: 2, 100: 4}
        self.row = row.get(val, 0)
        self.sprites = self.getSprites()
        self.position = pos
        self.rect = self.sprites[0].get_rect(topleft=self.position)
        self.currentTime = 0
        self.frameTime = 100
        self.currentFrame = 0

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
        self.rect.topleft = pos
        screen.blit(self.sprites[self.currentFrame], pos)

    def detectClick(self, event):
        x, y = event.pos
        if self.rect.collidepoint(x, y):
            return True
        return False
    
    
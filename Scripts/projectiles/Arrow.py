import pygame

class Arrow(pygame.sprite.Sprite):
    def __init__(self, image_path, speed_px_s=360, scale_px=None):
        super().__init__()
        img = pygame.image.load(image_path).convert_alpha()
        if scale_px:
            img = pygame.transform.smoothscale(img, scale_px)
        self.image = img
        self.rect = self.image.get_rect()
        self.vx = 0.0
        self.vy = -abs(speed_px_s)  
        self.alive = True

    def set_center(self, cx, cy):
        self.rect = self.image.get_rect(center=(cx, cy))

    def update(self, dt):
        if not self.alive:
            return
        self.rect.x += self.vx * dt
        self.rect.y += self.vy * dt

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

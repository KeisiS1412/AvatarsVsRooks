# projectiles/Sword.py
import pygame

class Sword:
    """
    Proyectil enemigo 'Sword' que viaja hacia arriba (como la flecha del flechero).
    Usa update(dt) con dt en segundos (tu Matrix ya divide bien a dt_enemies).
    """
    def __init__(self, image_path, speed_px_s=320, scale_px=None):
        img = pygame.image.load(image_path).convert_alpha()
        if scale_px is not None:
            img = pygame.transform.smoothscale(img, scale_px)
        self.image = img
        self.rect = self.image.get_rect()
        self.speed = speed_px_s
        self.damage = 3
        self.alive = True

    def set_center(self, cx, cy):
        self.rect.center = (cx, cy)

    def update(self, dt):
        # Viaja hacia arriba (y decrece)
        dy = -self.speed * dt
        self.rect.y += int(dy)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)

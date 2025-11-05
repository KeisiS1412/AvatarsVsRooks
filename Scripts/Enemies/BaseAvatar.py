# Enemies/BaseAvatar.py
import pygame

class BaseAvatar:
    """Clase base para enemigos/avatares con sistema de vida y barra de HP."""
    def __init__(self, hp: int, on_death=None):
        self.max_hp = int(hp)
        self.hp = int(hp)
        self.alive = True
        self.on_death = on_death  # callback opcional (Matrix puede usarlo)
        self.rect = pygame.Rect(0, 0, 0, 0)  # se ajusta desde la subclase

    # ---- lógica de vida ----
    def take_damage(self, amount: int):
        """Resta vida y destruye si llega a 0."""
        if not self.alive:
            return
        self.hp = max(0, self.hp - int(amount))
        if self.hp == 0:
            self.alive = False
            if callable(self.on_death):
                self.on_death(self)

    def heal(self, amount: int):
        if not self.alive:
            return
        self.hp = min(self.max_hp, self.hp + int(amount))

    def hp_ratio(self) -> float:
        return 0.0 if self.max_hp == 0 else self.hp / self.max_hp

    # ---- dibujar barra de vida encima ----
    def draw_hp_bar(self, screen):
        if not hasattr(self, "rect") or self.rect.width == 0:
            return

        bar_width = int(self.rect.width * 0.5)   # pequeña
        bar_height = 4
        x = self.rect.centerx - bar_width // 2
        y = self.rect.top - 8  # justo arriba del sprite

        pygame.draw.rect(screen, (60, 20, 20), (x, y, bar_width, bar_height))
        pygame.draw.rect(screen, (20, 220, 20), (x, y, int(bar_width * self.hp_ratio()), bar_height))

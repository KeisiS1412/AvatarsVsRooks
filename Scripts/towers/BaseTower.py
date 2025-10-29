# towers/BaseTower.py
import pygame

class BaseTower:
    def __init__(self, hp:int, on_destroy=None):
        self.max_hp = int(hp)
        self.hp = int(hp)
        self.alive = True
        self.on_destroy = on_destroy  # callback opcional (Matrix la puede usar)
        # info de grid (opcional pero útil)
        self.row = None
        self.col = None
        self.cell_size = None
        self.image_pos = None
        self.rect = pygame.Rect(0, 0, 0, 0)  # la subclase puede reemplazarlo con el rect de su sprite

    # vincula la torre a una celda de la matriz (para barras de vida, clics, etc.)
    def bind_grid(self, row, col, cell_size, image_pos, sprite_size=None):
        self.row, self.col = row, col
        self.cell_size = cell_size
        self.image_pos = image_pos
        x = image_pos[0] + col * cell_size[0]
        y = image_pos[1] + row * cell_size[1]
        if sprite_size is None:
            sprite_size = cell_size
        self.rect = pygame.Rect(x, y, sprite_size[0], sprite_size[1])

    # --- vida / daño ---
    def take_damage(self, amount: int):
        if not self.alive:
            return 0
        self.hp = max(0, self.hp - int(amount))
        if self.hp == 0:
            self.alive = False
            if callable(self.on_destroy):
                self.on_destroy(self)
        return self.hp

    def heal(self, amount: int):
        if not self.alive:
            return 0
        self.hp = min(self.max_hp, self.hp + int(amount))
        return self.hp

    def hp_ratio(self) -> float:
        return 0.0 if self.max_hp == 0 else self.hp / self.max_hp

    def draw_hp_bar(self, screen):
        """Dibuja una pequeña barra de vida encima de la torre."""
        if self.rect.width == 0:
            return  # no se ha definido el rect aún

        # Tamaño y posición de la barra
        bar_width = int(self.rect.width * 0.5)   # mitad del ancho de la torre
        bar_height = 4                           # muy delgada
        x = self.rect.centerx - bar_width // 2   # centrada horizontalmente
        y = self.rect.top - 8                    # 8 px por encima del sprite

        # Fondo oscuro (barra vacía)
        pygame.draw.rect(screen, (60, 20, 20), (x, y, bar_width, bar_height))

        # Vida restante (verde)
        filled_width = int(bar_width * self.hp_ratio())
        pygame.draw.rect(screen, (20, 220, 20), (x, y, filled_width, bar_height))

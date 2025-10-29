import pygame

class TowerButton:
    """Botón representando una torre con ícono estático (sin animación)."""

    def __init__(self, tower_type: str, icon_surface: pygame.Surface, rect: pygame.Rect):
        self.tower_type = tower_type
        self.icon = icon_surface
        self.rect = rect
        self.selected = False

        # Centramos el icono dentro del rect
        self._icon_pos = (
            self.rect.x + (self.rect.w - self.icon.get_width()) // 2,
            self.rect.y + (self.rect.h - self.icon.get_height()) // 2
        )

        # Estilos visuales
        self.slot_color = (40, 40, 46)
        self.border_color = (70, 70, 80)
        self.selected_color = (200, 160, 40)
        self._font = pygame.font.SysFont(None, 22)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Devuelve True si este botón fue clickeado (click izquierdo)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        # Fondo del botón
        pygame.draw.rect(screen, self.slot_color, self.rect, border_radius=10)
        # Borde base
        pygame.draw.rect(screen, self.border_color, self.rect, width=2, border_radius=10)
        # Borde de selección
        if self.selected:
            pygame.draw.rect(screen, self.selected_color, self.rect, width=3, border_radius=10)

        # Dibuja el icono
        screen.blit(self.icon, self._icon_pos)

        # Etiqueta
        label = self._font.render(self.tower_type.capitalize(), True, (230, 230, 235))
        screen.blit(label, (self.rect.x + 10, self.rect.y + 8))

import pygame
from .AssetsUtils import AssetsUtils
from .TowerButton import TowerButton
class ShopPanel:
    """Panel lateral derecho con botones para seleccionar el tipo de torre."""

    def __init__(self, screen_size: tuple[int, int]):
        self.screen_w, self.screen_h = screen_size
        self.width = 220
        self.rect = pygame.Rect(self.screen_w - self.width, 0, self.width, self.screen_h)

        # Colores del panel
        self.bg_color = (25, 25, 28)
        self.border_color = (60, 60, 70)
        self.title_color = (220, 220, 230)
        self._font = pygame.font.SysFont(None, 24)

        # Layout
        padding = 16
        slot_h = 90
        x = self.rect.x + padding
        y = self.rect.y + padding + 28
        w = self.width - 2 * padding

        # Cargar íconos de torres
        fire_icon = AssetsUtils.load_first_frame("Assets/towers/fire.png", 4, 2, (72, 72))
        # (Para cuando existan)
        water_icon = AssetsUtils.load_first_frame("Assets/towers/water2.png", 4, 2, (72, 72))
        sand_icon = AssetsUtils.load_first_frame("Assets/towers/sand.png", 4, 2, (72, 72))
        rock_icon = AssetsUtils.load_first_frame("Assets/towers/rock.png", 4, 2, (72, 72))

        # Crear botones
        self.buttons: list[TowerButton] = []
        self.buttons.append(TowerButton("fire", fire_icon, pygame.Rect(x, y, w, slot_h)))
        y += slot_h + padding
        self.buttons.append(TowerButton("water", water_icon, pygame.Rect(x, y, w, slot_h)))
        y += slot_h + padding
        self.buttons.append(TowerButton("sand", sand_icon, pygame.Rect(x, y, w, slot_h)))
        y += slot_h + padding
        self.buttons.append(TowerButton("rock", rock_icon, pygame.Rect(x, y, w, slot_h)))

        # Selección inicial
        self._selected_type = None
        self._sync_selection()

    def _sync_selection(self):
        """Actualiza visualmente cuál botón está seleccionado."""
        for button in self.buttons:
            button.selected = (button.tower_type == self._selected_type)

    def handle_event(self, event: pygame.event.Event) -> tuple[bool, bool]:
        """
        Procesa un evento de pygame.
        Retorna:
          (consumed, changed)
          consumed=True si el click fue dentro del panel
          changed=True si cambió la torre seleccionada
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                for button in self.buttons:
                    if button.handle_event(event):
                        if self._selected_type != button.tower_type:
                            self._selected_type = button.tower_type
                            self._sync_selection()
                            return True, True
                        return True, False
                return True, False
        return False, False

    def get_selected_type(self) -> str:
        """Devuelve el tipo de torre actualmente seleccionado."""
        return self._selected_type

    def draw(self, screen: pygame.Surface):
        """Dibuja el panel lateral completo."""
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        title = self._font.render("Torres", True, self.title_color)
        screen.blit(title, (self.rect.x + 16, self.rect.y + 10))

        for button in self.buttons:
            button.draw(screen)

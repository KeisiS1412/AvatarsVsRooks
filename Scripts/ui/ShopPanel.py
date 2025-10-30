import pygame
from .AssetsUtils import AssetsUtils
from .TowerButton import TowerButton
from towers.TowerFactory import TowerFactory
class ShopPanel:
    """Panel lateral derecho con botones para seleccionar el tipo de torre."""

    def __init__(self, screen_size: tuple[int, int]):
        self.screen_w, self.screen_h = screen_size
        self.width = 220
        self.rect = pygame.Rect(0, 0, self.width, self.screen_h)

        # Colores del panel
        self.bg_color = (25, 25, 28)
        self.border_color = (60, 60, 70)
        self.title_color = (220, 220, 230)
        self._font = pygame.font.SysFont(None, 24)

        # Layout
        padding = 16
        x = self.rect.x + padding
        y = self.rect.y + padding + 28
        w = self.width - 2 * padding

        slot_h = 220  
        icon_size = (100, 150)  # íconos más grandes y centrados

        fire_icon = AssetsUtils.load_first_frame("Assets/towers/fire.png", 4, 2, icon_size)
        water_icon = AssetsUtils.load_first_frame("Assets/towers/water2.png", 4, 2, icon_size)
        sand_icon = AssetsUtils.load_first_frame("Assets/towers/sand.png", 4, 2, icon_size)
        rock_icon = AssetsUtils.load_first_frame("Assets/towers/rock.png", 4, 2, icon_size)


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

    def _sync_selection(self): # Actualiza el estado de selección de los botones
        for button in self.buttons:
            button.selected = (button.tower_type == self._selected_type)

    def handle_event(self, event: pygame.event.Event) -> tuple[bool, bool]: # Maneja eventos de mouse, devuelve (consumido, cambió selección)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (1, 3):
            # Click derecho: cancelar selección si fue dentro del panel
            if event.button == 3 and self.rect.collidepoint(event.pos):
                prev = self._selected_type
                self._selected_type = None
                self._sync_selection()
                return True, (prev is not None)

            if self.rect.collidepoint(event.pos):
                for button in self.buttons:
                    if button.handle_event(event):
                        # Toggle: si ya estaba seleccionada, deselecciona
                        if self._selected_type == button.tower_type:
                            self._selected_type = None
                        else:
                            self._selected_type = button.tower_type
                        self._sync_selection()
                        return True, True
                return True, False
        return False, False


    def clear_selection(self): # Deselecciona la torre actualmente seleccionada
        if self._selected_type is not None:
            self._selected_type = None
            self._sync_selection()

    def get_selected_type(self) -> str: # Devuelve el tipo de torre actualmente seleccionado
        return self._selected_type

    def draw(self, screen: pygame.Surface): # Dibuja el panel y sus botones
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.border_color, self.rect, 2)

        title = self._font.render("Torres", True, self.title_color)
        screen.blit(title, (self.rect.x + 16, self.rect.y + 10))

        for button in self.buttons:
            button.draw(screen)

            price = TowerFactory.get_cost(button.tower_type)
            price_text = f"${price}"
            price_surf = self._font.render(price_text, True, (255, 220, 90))

            bx, by, bw, bh = button.rect
            text_x = bx + (bw - price_surf.get_width()) // 2
            text_y = by + bh - 25
            screen.blit(price_surf, (text_x, text_y))


import pygame

class Button:
    """Representa un botón interactivo que puede detectar clics y mostrar texto."""

    def __init__(self, x, y, width, height, text, font, normalColor, hoverColor, fontColor=(255, 255, 255)):  # Inicializa el botón con sus propiedades
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.text = text
        self.font = font
        self.normalColor = normalColor
        self.hoverColor = hoverColor  # Color de hover (no usado actualmente)
        self.currentColor = normalColor
        self.fontColor = fontColor

    def draw(self, screen, scrollOffset=0):  # Dibuja el botón en la pantalla
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.currentColor, adjRect, border_radius=8)
        textRender = self.font.render(self.text, True, self.fontColor)
        textRect = textRender.get_rect(center=adjRect.center)
        screen.blit(textRender, textRect)

    def update(self, mousePos, scrollOffset=0):  # Actualiza el estado del botón (hover eliminado)
        pass

    def wasClicked(self, event, scrollOffset=0):  # Verifica si el botón fue clickeado
        adjRect = self.rect.move(0, -scrollOffset)
        return event.type == pygame.MOUSEBUTTONDOWN and adjRect.collidepoint(event.pos)

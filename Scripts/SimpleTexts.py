import pygame

class SimpleText:
    """Muestra un texto simple en pantalla con opción de fondo y detección de clics."""

    def __init__(self, text, centerX, centerY, font, textColor=(0, 0, 0), bgColor=None, padding=10):  # Inicializa el texto
        self.text = text
        self.font = font
        self.textColor = textColor
        self.bgColor = bgColor
        self.padding = padding

        self.label = self.font.render(self.text, True, self.textColor)
        self.rect = self.label.get_rect()
        self.rect.center = (centerX, centerY)
        if self.bgColor:
            self.rect.inflate_ip(self.padding * 2, self.padding * 2)

    def draw(self, screen, scrollOffset=0):  # Dibuja el texto en pantalla
        adjRect = self.rect.move(0, -scrollOffset)
        if self.bgColor:
            pygame.draw.rect(screen, self.bgColor, adjRect, border_radius=8)
        screen.blit(self.label, self.label.get_rect(center=adjRect.center))

    def wasClicked(self, event, scrollOffset=0):  # Verifica si el texto fue clickeado
        adjRect = self.rect.move(0, -scrollOffset)
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and adjRect.collidepoint(event.pos)

    def setText(self, newText):  # Cambia el texto mostrado
        self.text = newText
        self.label = self.font.render(self.text, True, self.textColor)
        oldCenter = self.rect.center
        self.rect = self.label.get_rect()
        self.rect.center = oldCenter
        if self.bgColor:
            self.rect.inflate_ip(self.padding * 2, self.padding * 2)

    def update(self, deltaTime=0, scrollOffset=0):  # Método vacío para compatibilidad
        pass

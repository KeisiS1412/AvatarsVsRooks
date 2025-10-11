import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, normalColor, hoverColor, fontColor=(255, 255, 255)):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.text = text
        self.font = font
        self.normalColor = normalColor
        self.hoverColor = hoverColor  # Ya no se usa, pero puedes conservarlo si lo necesitas más adelante
        self.currentColor = normalColor
        self.fontColor = fontColor  

    def draw(self, screen, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.currentColor, adjRect, border_radius=8)
        textRender = self.font.render(self.text, True, self.fontColor)
        textRect = textRender.get_rect(center=adjRect.center)
        screen.blit(textRender, textRect)

    def update(self, mousePos, scrollOffset=0):
        pass  # Hover eliminado, no se actualiza el color

    def wasClicked(self, event, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        return event.type == pygame.MOUSEBUTTONDOWN and adjRect.collidepoint(event.pos)

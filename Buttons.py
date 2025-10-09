import pygame

class Button:
    def __init__(self, x, y, width, height, text, font, normalColor, hoverColor, fontColor=(255, 255, 255)):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.text = text
        self.font = font
        self.normalColor = normalColor
        self.hoverColor = hoverColor
        self.currentColor = normalColor
        self.fontColor = fontColor  

    def draw(self, screen):
        pygame.draw.rect(screen, self.currentColor, self.rect, border_radius=8)
        textRender = self.font.render(self.text, True, self.fontColor)
        textRect = textRender.get_rect(center=self.rect.center)
        screen.blit(textRender, textRect)

    def update(self, mousePos):
        self.currentColor = self.hoverColor if self.rect.collidepoint(mousePos) else self.normalColor

    def wasClicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)



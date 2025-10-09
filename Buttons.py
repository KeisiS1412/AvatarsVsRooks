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
        self.textColor = (0, 0, 0) 

    def draw(self, screen, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.currentColor, adjRect, border_radius=8)

        # Render del texto con color temable
        label = self.font.render(self.text, True, getattr(self, "textColor", (0, 0, 0)))
        label_rect = label.get_rect(center=adjRect.center)

        screen.blit(label, label_rect)

    def update(self, mousePos, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        self.isHover = adjRect.collidepoint(mousePos)
        self.currentColor = self.overColor if self.isHover else self.normalColor

    def wasClicked(self, event, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        return event.type == pygame.MOUSEBUTTONDOWN and adjRect.collidepoint(event.pos)

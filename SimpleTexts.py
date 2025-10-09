import pygame

class SimpleText:
    def __init__(self, text, centerX, centerY, font, textColor=(0, 0, 0), bgColor=None, padding=10):
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

    def draw(self, screen):
        if self.bgColor:
            pygame.draw.rect(screen, self.bgColor, self.rect, border_radius=8)
        screen.blit(self.label, self.label.get_rect(center=self.rect.center))

    def wasClicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def setText(self, newText):
        self.text = newText
        self.label = self.font.render(self.text, True, self.textColor)
        oldCenter = self.rect.center
        self.rect = self.label.get_rect()
        self.rect.center = oldCenter
        if self.bgColor:
            self.rect.inflate_ip(self.padding * 2, self.padding * 2)
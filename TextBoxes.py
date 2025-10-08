import pygame

class TextBox:
    def __init__(self, x, y, width, height, font, inactiveColor, activeColor, initialText=""):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.inactiveColor = inactiveColor
        self.activeColor = activeColor
        self.currentColor = self.inactiveColor
        self.text = initialText
        self.font = font
        self.isActive = False
        self.cursorVisible = True
        self.cursorTimer = 0
        self.cursorInterval = 500

    def draw(self, screen, deltaTime):
        pygame.draw.rect(screen, self.currentColor, self.rect, border_radius=8)
        textSurface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(textSurface, (self.rect.x + 5, self.rect.y + 5))

        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0

            if self.cursorVisible:
                cursorX = self.rect.x + 5 + textSurface.get_width()
                cursorY = self.rect.y + 5
                cursorHeight = textSurface.get_height()
                pygame.draw.line(screen, (0, 0, 0), (cursorX, cursorY), (cursorX, cursorY + cursorHeight), 2)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.isActive = self.rect.collidepoint(event.pos)
            self.currentColor = self.activeColor if self.isActive else self.inactiveColor

        if event.type == pygame.KEYDOWN and self.isActive:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.isActive = False
                self.currentColor = self.inactiveColor
            else:
                self.text += event.unicode

    def getText(self):
        return self.text

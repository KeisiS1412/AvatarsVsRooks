import pygame

class TextBox:
    def __init__(self, x, y, width, height, font, inactiveColor, activeColor, initialText="",
                 content_offset_y=10, border_radius=8):
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
        self.content_offset_y = content_offset_y
        self.border_radius = border_radius

        self.isInvalid = False
        self.errorBorderColor = (255, 0, 0)  # rojo para indicar error
        self.isPassword = False
        self.showPassword = False

    def draw(self, screen, deltaTime=0, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.currentColor, adjRect, border_radius=8)
        borderColor = self.errorBorderColor if self.isInvalid else (0, 0, 0)
        pygame.draw.rect(screen, borderColor, adjRect, width=2, border_radius=8)

        padding = 10
        maxTextWidth = adjRect.width - padding * 2
        displayText = self.text if not (self.isPassword and not self.showPassword) else "•" * len(self.text)

        textToRender = displayText
        while self.font.size(textToRender)[0] > maxTextWidth and len(textToRender) > 0:
            textToRender = textToRender[1:]

        visibleSurface = self.font.render(textToRender, True, (0, 0, 0))
        screen.blit(visibleSurface, (adjRect.x + padding, adjRect.y + padding))

        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0

            if self.cursorVisible:
                cursorX = adjRect.x + padding + visibleSurface.get_width()
                cursorY = adjRect.y + padding
                cursorHeight = visibleSurface.get_height()
                pygame.draw.line(screen, (0, 0, 0), (cursorX, cursorY), (cursorX, cursorY + cursorHeight), 2)

    def handleEvent(self, event, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if adjRect.collidepoint(event.pos):
                self.isActive = True
                self.currentColor = self.activeColor
                self.isInvalid = False
            else:
                self.isActive = False
                self.currentColor = self.inactiveColor

        if event.type == pygame.KEYDOWN and self.isActive:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.isActive = False
                self.currentColor = self.inactiveColor
            else:
                self.text += event.unicode

    def update(self, deltaTime=0, scrollOffset=0):
        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0

    def getText(self):
        return self.text

    def markInvalid(self):
        self.isInvalid = True

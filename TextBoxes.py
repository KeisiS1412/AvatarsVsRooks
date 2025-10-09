import pygame

class TextBox:
    def __init__(self, x, y, width, height, font, inactiveColor, activeColor, initialText="", errorBorderColor=(255, 0, 0), isPassword=False):
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
        self.errorBorderColor = errorBorderColor
        self.isInvalid = False
        self.isPassword = isPassword
        self.showPassword = False

    def draw(self, screen, deltaTime):
        pygame.draw.rect(screen, self.currentColor, self.rect, border_radius=8)
        borderColor = self.errorBorderColor if self.isInvalid else (0, 0, 0)
        pygame.draw.rect(screen, borderColor, self.rect, width=2, border_radius=8)

        padding = 10
        maxTextWidth = self.rect.width - padding * 2

        displayText = self.text
        if self.isPassword and not self.showPassword:
            displayText = "•" * len(self.text)

        fullTextSurface = self.font.render(displayText, True, (0, 0, 0))
        fullWidth = fullTextSurface.get_width()

        if fullWidth <= maxTextWidth:
            textToRender = displayText
        else:
            textToRender = displayText
            while self.font.size(textToRender)[0] > maxTextWidth and len(textToRender) > 0:
                textToRender = textToRender[1:]

        visibleSurface = self.font.render(textToRender, True, (0, 0, 0))
        screen.blit(visibleSurface, (self.rect.x + padding, self.rect.y + padding))

        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0

            if self.cursorVisible:
                cursorX = self.rect.x + padding + visibleSurface.get_width()
                cursorY = self.rect.y + padding
                cursorHeight = visibleSurface.get_height()
                pygame.draw.line(screen, (0, 0, 0), (cursorX, cursorY), (cursorX, cursorY + cursorHeight), 2)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
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
            elif event.key == pygame.K_TAB and self.isPassword:
                self.showPassword = not self.showPassword
            else:
                self.text += event.unicode

    def update(self, deltaTime):
        if self.isActive:
            self.cursorTimer += deltaTime
            if self.cursorTimer >= self.cursorInterval:
                self.cursorVisible = not self.cursorVisible
                self.cursorTimer = 0

    def getText(self):
        return self.text

    def markInvalid(self):
        self.isInvalid = True


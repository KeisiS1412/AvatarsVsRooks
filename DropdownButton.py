import pygame

class DropdownButton:
    def __init__(self, centerX, centerY, width, height, font, options, textColor, bgColor, hoverColor, placeholder, maxVisible=3):
        self.optionHeight = height
        self.font = font
        self.options = options
        self.textColor = textColor
        self.bgColor = bgColor
        self.hoverColor = hoverColor
        self.maxVisible = maxVisible
        self.expanded = False
        self.selected = options[0]
        self.scrollOffset = 0
        self.placeholder = placeholder
        self.selected = None

        # Centrado automático
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (centerX, centerY)

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.expanded = not self.expanded
            elif self.expanded:
                for i in range(self.scrollOffset, min(len(self.options), self.scrollOffset + self.maxVisible)):
                    optionRect = pygame.Rect(self.rect.x, self.rect.y + (i - self.scrollOffset + 1) * self.optionHeight, self.rect.width, self.optionHeight)
                    if optionRect.collidepoint(event.pos):
                        self.selected = self.options[i]
                        self.expanded = False
                        break
                else:
                    self.expanded = False
        elif event.type == pygame.MOUSEWHEEL and self.expanded:
            mouseX, mouseY = pygame.mouse.get_pos()
            menuTop = self.rect.bottom
            menuBottom = self.rect.bottom + self.optionHeight * min(len(self.options), self.maxVisible)
            menuRect = pygame.Rect(self.rect.x, menuTop, self.rect.width, menuBottom - menuTop)

            if menuRect.collidepoint((mouseX, mouseY)):
                self.scrollOffset = max(0, min(self.scrollOffset - event.y, len(self.options) - self.maxVisible))

    def update(self, mousePos):
        pass

    def draw(self, screen, deltaTime=0):
        # Fondo del botón
        pygame.draw.rect(screen, self.bgColor, self.rect, border_radius=10)
        # Borde negro
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=2, border_radius=10)

        # Texto seleccionado
        displayText = self.selected if self.selected else self.placeholder
        label = self.font.render(displayText, True, self.textColor)
        screen.blit(label, (self.rect.x + 10, self.rect.y + (self.rect.height - label.get_height()) // 2))

        # Opciones desplegadas
        if self.expanded:
            for i in range(self.scrollOffset, min(len(self.options), self.scrollOffset + self.maxVisible)):
                optionRect = pygame.Rect(
                    self.rect.x,
                    self.rect.y + (i - self.scrollOffset + 1) * self.optionHeight,
                    self.rect.width,
                    self.optionHeight
                )
                mousePos = pygame.mouse.get_pos()
                color = self.hoverColor if optionRect.collidepoint(mousePos) else self.bgColor

                pygame.draw.rect(screen, color, optionRect, border_radius=10)
                pygame.draw.rect(screen, (0, 0, 0), optionRect, width=2, border_radius=10)

                optionLabel = self.font.render(self.options[i], True, self.textColor)
                screen.blit(optionLabel, (optionRect.x + 10, optionRect.y + (optionRect.height - optionLabel.get_height()) // 2))


    def getText(self):
        return self.selected

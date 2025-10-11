import pygame

class DropdownButton:
    """Menú desplegable con desplazamiento para selección de opciones."""

    def __init__(self, centerX, centerY, width, height, font, options, textColor, bgColor, hoverColor, placeholder, maxVisible=3):  # Inicializa el menú desplegable
        self.optionHeight = height
        self.font = font
        self.options = options
        self.textColor = textColor
        self.bgColor = bgColor
        self.hoverColor = hoverColor
        self.maxVisible = maxVisible
        self.expanded = False
        self.scrollOffset = 0
        self.placeholder = placeholder
        self.selected = None
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (centerX, centerY)

    def handleEvent(self, event, scrollOffset=0):  # Maneja clics y desplazamiento del menú
        adjRect = self.rect.move(0, -scrollOffset)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if adjRect.collidepoint(event.pos):
                self.expanded = not self.expanded
            elif self.expanded:
                clickedOption = False
                for i in range(self.scrollOffset, min(len(self.options), self.scrollOffset + self.maxVisible)):
                    optionRect = pygame.Rect(
                        adjRect.x,
                        adjRect.y + (i - self.scrollOffset + 1) * self.optionHeight,
                        adjRect.width,
                        self.optionHeight
                    )
                    if optionRect.collidepoint(event.pos):
                        self.selected = self.options[i]
                        clickedOption = True
                        break
                self.expanded = False if not clickedOption else self.expanded
            else:
                self.expanded = False

        elif event.type == pygame.MOUSEWHEEL and self.expanded:
            mouseX, mouseY = pygame.mouse.get_pos()
            menuTop = adjRect.bottom
            menuHeight = self.optionHeight * min(len(self.options), self.maxVisible)
            menuRect = pygame.Rect(adjRect.x, menuTop, adjRect.width, menuHeight)
            if menuRect.collidepoint((mouseX, mouseY)) or adjRect.collidepoint((mouseX, mouseY)):
                maxOffset = max(0, len(self.options) - self.maxVisible)
                self.scrollOffset = max(0, min(self.scrollOffset - event.y, maxOffset))

    def draw(self, screen, deltaTime=0, scrollOffset=0):  # Dibuja el botón principal y las opciones visibles
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.bgColor, adjRect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), adjRect, width=2, border_radius=8)

        displayText = self.selected if self.selected else self.placeholder
        label = self.font.render(displayText, True, self.textColor)
        screen.blit(label, (adjRect.x + 10, adjRect.y + (adjRect.height - label.get_height()) // 2))

        if self.expanded:
            visibleOptions = self.options[self.scrollOffset:self.scrollOffset + self.maxVisible]
            for i, option in enumerate(visibleOptions):
                optionRect = pygame.Rect(
                    adjRect.x,
                    adjRect.bottom + i * self.optionHeight,
                    adjRect.width,
                    self.optionHeight
                )
                mousePos = pygame.mouse.get_pos()
                color = self.hoverColor if optionRect.collidepoint(mousePos) else self.bgColor
                pygame.draw.rect(screen, color, optionRect, border_radius=8)
                pygame.draw.rect(screen, (0, 0, 0), optionRect, width=2, border_radius=8)
                optionLabel = self.font.render(option, True, self.textColor)
                screen.blit(optionLabel, (optionRect.x + 10, optionRect.y + (optionRect.height - optionLabel.get_height()) // 2))

            totalHeight = self.optionHeight * len(visibleOptions)
            pygame.draw.rect(screen, (0, 0, 0), (adjRect.x, adjRect.bottom, adjRect.width, totalHeight), width=2, border_radius=8)

    def update(self, deltaTime=0, scrollOffset=0):  # Mantiene compatibilidad con otras escenas
        pass

    def getText(self):  # Retorna el texto seleccionado
        return self.selected

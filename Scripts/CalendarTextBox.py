import pygame
from Scripts.TextBoxes import TextBox
from datetime import datetime

class CalendarTextBox(TextBox):
    def __init__(self, x, y, width, height, font, inactiveColor, activeColor, label):
        super().__init__(x, y, width, height, font, inactiveColor, activeColor, label)
        self.openMenu = False
        self.selectedDay = 1
        self.selectedMonth = 1
        self.selectedYear = datetime.now().year

        # Dimensiones del calendario
        self.calWidth = 250
        self.calHeight = 200
        self.calRect = pygame.Rect(0, 0, self.calWidth, self.calHeight)

        # Colores
        self.bgColor = (200, 200, 200)
        self.borderColor = (0, 0, 0)
        self.highlightColor = (150, 150, 250)

        # Posición relativa al textbox
        self.calRect.topleft = (self.rect.right + 10, self.rect.top)

        # Listas de selección
        self.days = [str(i) for i in range(1, 32)]
        self.months = [str(i) for i in range(1, 13)]
        self.years = [str(y) for y in range(1900, datetime.now().year + 1)]

    def handleEvent(self, event, scrollOffset=0):
        super().handleEvent(event, scrollOffset)
        adjRect = self.rect.move(0, -scrollOffset)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if adjRect.collidepoint(event.pos):
                self.openMenu = not self.openMenu
            elif self.openMenu and self.calRect.collidepoint(event.pos):
                x, y = event.pos
                relX, relY = x - self.calRect.x, y - self.calRect.y

                # Dividimos la zona del calendario en 3 columnas: día, mes, año
                colWidth = self.calWidth // 3
                rowHeight = 20

                col = relX // colWidth
                row = relY // rowHeight

                if col == 0 and row < len(self.days):
                    self.selectedDay = int(self.days[row])
                elif col == 1 and row < len(self.months):
                    self.selectedMonth = int(self.months[row])
                elif col == 2 and row < len(self.years):
                    self.selectedYear = int(self.years[row])

                # Si se hace click en la última fila, asumimos aceptar
                if row >= max(len(self.days), len(self.months), len(self.years)):
                    self.text = f"{self.selectedDay}/{self.selectedMonth}/{self.selectedYear}"
                    self.openMenu = False
            else:
                self.openMenu = False

        elif event.type == pygame.KEYDOWN and self.openMenu:
            if event.key == pygame.K_ESCAPE:
                self.openMenu = False

    def draw(self, screen, deltaTime=0, scrollOffset=0):
        super().draw(screen, deltaTime, scrollOffset)
        if self.openMenu:
            self.calRect.topleft = (self.rect.right + 10, self.rect.top - scrollOffset)
            pygame.draw.rect(screen, self.bgColor, self.calRect)
            pygame.draw.rect(screen, self.borderColor, self.calRect, 2)

            colWidth = self.calWidth // 3
            rowHeight = 20

            # Dibujar días
            for i, day in enumerate(self.days):
                color = self.highlightColor if int(day) == self.selectedDay else (0, 0, 0)
                textSurf = self.font.render(day, True, color)
                screen.blit(textSurf, (self.calRect.x + 5, self.calRect.y + i * rowHeight))

            # Dibujar meses
            for i, month in enumerate(self.months):
                color = self.highlightColor if int(month) == self.selectedMonth else (0, 0, 0)
                textSurf = self.font.render(month, True, color)
                screen.blit(textSurf, (self.calRect.x + colWidth + 5, self.calRect.y + i * rowHeight))

            # Dibujar años
            for i, year in enumerate(self.years[-15:]):  # Mostrar últimos 15 años
                yVal = int(year)
                color = self.highlightColor if yVal == self.selectedYear else (0, 0, 0)
                textSurf = self.font.render(str(year), True, color)
                screen.blit(textSurf, (self.calRect.x + 2 * colWidth + 5, self.calRect.y + i * rowHeight))

# Scripts/CalendarTextBox.py
import pygame, calendar
from datetime import datetime
from TextBoxes import TextBox

# --- Dimensiones del popup ---
POP_W, POP_H   = 450, 290
HEADER_H       = 44
YEAR_WHEEL_W   = 90
CELL_W, CELL_H = 38, 28
PAD_X, PAD_Y   = 10, 8

# --- Texto del encabezado y semana ---
MONTHS = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]
WDAYS = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]  # Domingo a Sábado

class CalendarTextBox(TextBox):
    """
    TextBox con selector de fecha:
      - Flechas ◀ ▶ para cambiar mes
      - "Rueda" de año (click arriba/abajo o con rueda del mouse)
      - Grilla de días clicables
    El valor escrito en el TextBox queda como dd/mm/yyyy.
    """
    def __init__(self, x, y, width, height, font, inactiveColor, activeColor, label):
        super().__init__(x, y, width, height, font, inactiveColor, activeColor, label)
        now = datetime.now()
        self.openMenu = False 
        # Fecha seleccionada
        self.selectedDay   = now.day
        self.selectedMonth = now.month
        self.selectedYear  = now.year

        # Colores UI
        self.bg      = (245, 245, 245)
        self.bg2     = (232, 232, 232)
        self.border  = (160, 160, 160)
        self.accent  = (40, 120, 220)
        self.text_c  = (30, 30, 30)
        self.muted   = (120, 120, 120)
        self.day_bg  = (248, 248, 248)
        self.day_bor = (220, 220, 220)

        # Popup y zonas clicables
        self.popup      = pygame.Rect(0, 0, POP_W, POP_H)
        self.leftArrow  = pygame.Rect(0, 0, 32, HEADER_H)
        self.rightArrow = pygame.Rect(0, 0, 32, HEADER_H)
        self.yearWheel  = pygame.Rect(0, 0, YEAR_WHEEL_W, POP_H - HEADER_H - 12)

        # Celdas de días de la grilla
        self.dayCells = []  # lista[(pygame.Rect, int)]

        # Fuente pequeña para labels de días de la semana
        self.small = pygame.font.Font(None, 20)

    # ---------- Utilidades internas ----------
    def _first_wday_and_ndays(self, y, m):
        """Devuelve (primer_dia_semana_domingo0, num_dias)."""
        first_wday_mon0, ndays = calendar.monthrange(y, m)  # 0=Mon..6=Sun
        first_wday_sun0 = (first_wday_mon0 + 1) % 7
        return first_wday_sun0, ndays

    def _layout_regions(self):
        """Posiciona flechas y rueda de año dentro del popup."""
        px, py = self.popup.x, self.popup.y
        # Flechas en el header
        self.leftArrow.topleft   = (px + 6, py + 6)
        self.rightArrow.topright = (px + self.popup.w - 6, py + 6)
        # Rueda de años centrada bajo el header
        self.yearWheel.width  = YEAR_WHEEL_W
        self.yearWheel.height = POP_H - HEADER_H - 12
        self.yearWheel.topright = (self.popup.right - 25, py + HEADER_H + 6)

    def _weekday_labels(self):
        """Devuelve superficies y posiciones de Sun..Sat."""
        labels = []
        px, py = self.popup.x, self.popup.y
        x0 = px + PAD_X
        y0 = py + HEADER_H + 8
        for c, lbl in enumerate(WDAYS):
            surf = self.small.render(lbl, True, self.muted)
            pos  = (x0 + c*CELL_W + (CELL_W - surf.get_width())//2, y0 + 2)
            labels.append((surf, pos))
        return labels

    def _rebuild_day_cells(self):
        """Reconstruye self.dayCells para el mes/año seleccionados."""
        self.dayCells.clear()
        px, py = self.popup.x, self.popup.y
        start, ndays = self._first_wday_and_ndays(self.selectedYear, self.selectedMonth)
        # top-left de la grilla de días (bajo los labels de la semana)
        grid_x0 = px + PAD_X
        grid_y0 = py + HEADER_H + 8 + 24  # 24px de alto para labels de Sun..Sat

        row = 0
        col = start  # 0..6 (domingo..sábado)
        for d in range(1, ndays + 1):
            rx = grid_x0 + col * CELL_W
            ry = grid_y0 + row * CELL_H
            rect = pygame.Rect(rx, ry, CELL_W - 2, CELL_H - 2)
            self.dayCells.append((rect, d))
            col += 1
            if col == 7:
                col = 0
                row += 1

    def _month_title(self):
        return MONTHS[self.selectedMonth - 1]

    def _write_value(self):
        """Escribe la fecha seleccionada en formato dd/mm/yyyy."""
        dd = f"{self.selectedDay:02d}"
        mm = f"{self.selectedMonth:02d}"
        yyyy = f"{self.selectedYear:04d}"
        self.text = f"{dd}/{mm}/{yyyy}"

    # ---------- Eventos ----------
    def handleEvent(self, event, scrollOffset=0):
        # Mantén comportamiento base del TextBox (focus, etc.)
        super().handleEvent(event, scrollOffset)
        adjRect = self.rect.move(0, -scrollOffset)

        # Toggle del popup al clickear el textbox
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if adjRect.collidepoint(event.pos):
                self.openMenu = not self.openMenu
                if self.openMenu:
                    # Prepara layout y celdas inmediatamente
                    self.popup.topleft = (self.rect.right + 10, self.rect.top - scrollOffset)
                    self._layout_regions()
                    self._rebuild_day_cells()
                return

        if not self.openMenu:
            return

        # Con popup abierto: mantener layout y celdas siempre actualizados
        self.popup.topleft = (self.rect.right + 10, self.rect.top - scrollOffset)
        self._layout_regions()
        self._rebuild_day_cells()

        # Cerrar si clic fuera del popup
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.popup.collidepoint(event.pos):
                self.openMenu = False
                return

            # 1) Primero: click en un día (para que no se confunda con flechas)
            for rect, d in self.dayCells:
                if rect.collidepoint(event.pos):
                    self.selectedDay = d
                    self._write_value()
                    self.openMenu = False
                    return

            # 2) Flechas de mes
            if self.leftArrow.collidepoint(event.pos):
                self.selectedMonth -= 1
                if self.selectedMonth == 0:
                    self.selectedMonth = 12
                    self.selectedYear -= 1
                self._rebuild_day_cells()
                return

            if self.rightArrow.collidepoint(event.pos):
                self.selectedMonth += 1
                if self.selectedMonth == 13:
                    self.selectedMonth = 1
                    self.selectedYear += 1
                self._rebuild_day_cells()
                return

            # 3) Click en la “rueda” de años: arriba = -1, abajo = +1
            if self.yearWheel.collidepoint(event.pos):
                cy = self.yearWheel.centery
                y  = event.pos[1]
                if y < cy - 14:
                    self.selectedYear -= 1
                elif y > cy + 14:
                    self.selectedYear += 1
                self._rebuild_day_cells()
                return

        # Rueda del mouse para cambiar año si está sobre la “rueda”
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.yearWheel.collidepoint((mx, my)):
                self.selectedYear += event.y  # arriba=positivo
                self._rebuild_day_cells()
                return

        # ESC para cerrar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.openMenu = False

    # ---------- Dibujo ----------
    def draw(self, screen, deltaTime=0, scrollOffset=0):
        # Dibuja el TextBox “normal”
        super().draw(screen, deltaTime, scrollOffset)

    def draw_overlay(self, screen, scrollOffset=0):
        """Dibuja el popup por ENCIMA de todo (llamar al final del render de la escena)."""
        if not self.openMenu:
            return

        # Colocar popup junto al textbox; evitar que se salga de la ventana
        self.popup.topleft = (self.rect.right + 10, self.rect.top - scrollOffset)
        sw, sh = screen.get_size()
        if self.popup.right > sw - 6:
            self.popup.right = sw - 6
        if self.popup.bottom > sh - 6:
            self.popup.bottom = sh - 6
        self._layout_regions()

        # Panel + borde
        pygame.draw.rect(screen, self.bg, self.popup, border_radius=6)
        pygame.draw.rect(screen, self.border, self.popup, 2, border_radius=6)

        # Header
        header = pygame.Rect(self.popup.x, self.popup.y, self.popup.w, HEADER_H)
        pygame.draw.rect(screen, self.bg2, header, border_radius=6)

        # Flechas (triángulos)
        pygame.draw.polygon(screen, self.text_c, [
            (self.leftArrow.right-6, self.leftArrow.centery),
            (self.leftArrow.right-2, self.leftArrow.centery-8),
            (self.leftArrow.right-2, self.leftArrow.centery+8),
        ])
        pygame.draw.polygon(screen, self.text_c, [
            (self.rightArrow.left+6, self.rightArrow.centery),
            (self.rightArrow.left+2, self.rightArrow.centery-8),
            (self.rightArrow.left+2, self.rightArrow.centery+8),
        ])

        # Título del mes (a la izquierda de la rueda)
        t_month = self._month_title()
        t_surf  = self.font.render(t_month, True, self.text_c)
        screen.blit(
            t_surf,
            (self.yearWheel.left - 8 - t_surf.get_width(),
             self.popup.y + (HEADER_H - t_surf.get_height()) // 2)
        )

        # Rueda de años
        pygame.draw.rect(screen, (250, 250, 250), self.yearWheel, border_radius=6)
        pygame.draw.rect(screen, self.border, self.yearWheel, 1, border_radius=6)

        center_year = self.selectedYear
        years = [center_year-2, center_year-1, center_year, center_year+1, center_year+2]
        for i, y in enumerate(years):
            ys = self.font.render(str(y), True, self.text_c if y == center_year else self.muted)
            cx = self.yearWheel.centerx
            cy = self.yearWheel.centery + (i - 2) * 32
            screen.blit(ys, (cx - ys.get_width() // 2, cy - ys.get_height() // 2))

        # Banda de highlight en el centro de la rueda
        band = pygame.Rect(self.yearWheel.x, self.yearWheel.centery - 14, self.yearWheel.w, 28)
        pygame.draw.rect(screen, (230, 230, 230), band, border_radius=6)

        # Labels de días de la semana
        for surf, pos in self._weekday_labels():
            screen.blit(surf, pos)

        # Celdas de días + números
        self._rebuild_day_cells()
        for rect, d in self.dayCells:
            if d == self.selectedDay:
                pygame.draw.rect(screen, self.accent, rect, border_radius=4)
                col = (255, 255, 255)
            else:
                pygame.draw.rect(screen, self.day_bg, rect, border_radius=4)
                pygame.draw.rect(screen, self.day_bor, rect, 1, border_radius=4)
                col = self.text_c

            ds = self.small.render(str(d), True, col)
            screen.blit(ds, (rect.centerx - ds.get_width() // 2,
                             rect.centery - ds.get_height() // 2))

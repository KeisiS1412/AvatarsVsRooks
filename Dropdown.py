import pygame

class Dropdown:
    def __init__(self, x, y, w, h, font, options, initial_index=0,
                 color_bg=(230,230,230), color_hover=(210,210,210), color_text=(0,0,0),
                 border_radius=8, content_offset_y=10, title="", title_font=None, title_color=(0,0,0), title_offset_y = 45):
        self.rect = pygame.Rect(0, 0, w, h); self.rect.center = (x, y)
        self.font = font
        self.options = options[:]
        self.index = max(0, min(initial_index, len(options)-1))
        self.open = False

        # colores “temeables”
        self.color_bg = color_bg
        self.color_hover = color_hover
        self.color_text = color_text
        self.border_color = (180,180,180)   # NUEVO
        self.arrow_color  = (80,80,80)      # NUEVO

        self.border_radius = border_radius
        self.item_height = h
        self.content_offset_y = content_offset_y
        self.title_offset_y = title_offset_y

        self.title = title
        self.title_font = pygame.font.Font("Avenir.ttf", 24) if title_font is None else title_font
        self.title_color = title_color

        self.arrow_rect = pygame.Rect(self.rect.right - h, self.rect.top, h, h)
        self.button_bg   = self.color_bg      # color del botón (flecha)
        self.button_hover= self.color_hover

    @property
    def value(self):
        return self.options[self.index] if self.options else ""

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.arrow_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.open = not self.open
            elif self.open:
                for i, r in enumerate(self._items_rects()):
                    if r.collidepoint(event.pos):
                        self.index = i
                        self.open = False
                        break
                else:
                    self.open = False

    def update(self, _dt):
        pass

    def draw(self, s):
        # fondo principal
        pygame.draw.rect(s, self.color_bg, self.rect, border_radius=self.border_radius)

        # texto seleccionado
        txt = self.font.render(self.value, True, self.color_text)
        s.blit(txt, (self.rect.x+20, self.rect.y + 45))

        # botón flecha (usa color_bg, no gris fijo)
        hover_arrow = self.arrow_rect.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(
            s,
            self.button_hover if hover_arrow else self.button_bg,
            self.arrow_rect,
            border_radius=self.border_radius
        )
        cx = self.arrow_rect.centerx; cy = self.arrow_rect.centery
        pygame.draw.polygon(s, self.arrow_color, [(cx-8, cy-3), (cx+8, cy-3), (cx, cy+7)])

        # borde
        pygame.draw.rect(s, self.border_color, self.rect, width=2, border_radius=self.border_radius)

        # título
        title_surface = self.title_font.render(self.title, True, self.title_color)
        s.blit(title_surface, (self.rect.x + 20, self.rect.y - title_surface.get_height() + self.title_offset_y))

        # lista desplegada
        if self.open:
            for i, r in enumerate(self._items_rects()):
                hover = r.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(s, self.color_hover if hover else self.color_bg, r, border_radius=self.border_radius)
                t = self.font.render(self.options[i], True, self.color_text)
                s.blit(t, (r.x+20, r.y + (r.h - t.get_height())//2))

    def _items_rects(self):
        rects = []
        option_height = 55
        for i, _ in enumerate(self.options):
            r = pygame.Rect(self.rect.x, self.rect.bottom + 3 + i*option_height, self.rect.w, 52)
            rects.append(r)
        return rects


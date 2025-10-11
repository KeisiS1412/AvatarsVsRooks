import pygame

class Dropdown:
    def __init__(self, x, y, w, h, font, options, *,
                 initial_index=0,
                 textColor=(0, 0, 0),
                 bgColor=(230, 230, 230),
                 hoverColor=(210, 210, 210),
                 borderColor=(180, 170, 170),
                 border_radius=8,
                 content_offset_y=10,
                 title="",
                 title_font=None,
                 title_color=(0, 0, 0),
                 title_offset_y=45):
        
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = (x, y)
        self.font = font
        self.options = options[:]
        self.index = max(0, min(initial_index, len(options) - 1))
        self.open = False

        self.color_text = textColor
        self.color_bg = bgColor
        self.color_hover = hoverColor
        self.color_border = borderColor
        self.border_radius = border_radius
        self.item_height = h
        self.content_offset_y = content_offset_y
        self.title_offset_y = title_offset_y

        self.title = title
        self.title_font = pygame.font.Font("Avenir.ttf", 24) if title_font is None else title_font
        self.title_color = title_color

        self.arrow_rect = pygame.Rect(self.rect.right - h, self.rect.top, h, h)

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
        pygame.draw.rect(s, self.color_bg, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(s, self.color_border, self.rect, width=2, border_radius=self.border_radius)

        txt = self.font.render(self.value, True, self.color_text)
        s.blit(txt, (self.rect.x + 20, self.rect.y + 45))

        pygame.draw.rect(s, (200, 200, 200), self.arrow_rect, border_radius=self.border_radius)
        cx = self.arrow_rect.centerx
        cy = self.arrow_rect.centery
        pygame.draw.polygon(s, (80, 80, 80), [(cx - 8, cy - 3), (cx + 8, cy - 3), (cx, cy + 7)])

        if self.title:
            title_surface = self.title_font.render(self.title, True, self.title_color)
            s.blit(title_surface, (self.rect.x + 20, self.rect.y - title_surface.get_height() + self.title_offset_y))

        if self.open:
            for i, r in enumerate(self._items_rects()):
                hover = r.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(s, self.color_hover if hover else self.color_bg, r, border_radius=self.border_radius)
                pygame.draw.rect(s, self.color_border, r, width=2, border_radius=self.border_radius)
                t = self.font.render(self.options[i], True, self.color_text)
                s.blit(t, (r.x + 20, r.y + (r.h - t.get_height()) // 2))

    def _items_rects(self):
        rects = []
        option_height = 55
        for i, _ in enumerate(self.options):
            r = pygame.Rect(self.rect.x, self.rect.bottom + 3 + i * option_height, self.rect.w, 52)
            rects.append(r)
        return rects

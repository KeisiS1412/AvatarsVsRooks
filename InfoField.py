import pygame

class InfoField:
    def __init__(self, x, y, w, h, font, title, value="",
                 title_font=None, title_color=(120,120,120),
                 text_color=(0,0,0), bg=(240,240,240),
                 border_radius=8, content_offset_y=1000):
        self.title = title
        self.value = value
        self.font = font
        self.title_font = title_font or pygame.font.Font(None, 24)  # título más pequeño
        self.rect = pygame.Rect(0,0,w,h); self.rect.center=(x,y)
        self.radius = border_radius
        self.title_color = title_color
        self.text_color = text_color
        self.bg = bg
        self.content_offset_y = content_offset_y
        self.border_color = (180,180,180)  # nuevo

    def set_value(self, v):
        self.value = v

    def draw(self, s):
        # 1) fondo de la tarjeta/caja
        pygame.draw.rect(s, self.bg, self.rect, border_radius=self.radius)

        # 2) borde con el color de tema (NO gris fijo)
        pygame.draw.rect(s, self.border_color, self.rect, width=2, border_radius=self.radius)

        # 3) valor
        val = self.font.render(self.value, True, self.text_color)
        s.blit(val, (self.rect.x + 20, self.rect.y + 45))

        # 4) título
        title_surface = self.title_font.render(self.title, True, self.title_color)
        s.blit(title_surface, (self.rect.x + 20, self.rect.y - title_surface.get_height() + 45))


        


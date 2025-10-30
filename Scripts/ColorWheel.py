import pygame, math

def hsv_to_rgb(h, s, v):
    i = int(h*6)
    f = h*6 - i
    p = int(255*v*(1 - s))
    q = int(255*v*(1 - f*s))
    t = int(255*v*(1 - (1 - f)*s))
    v = int(255*v)
    i = i % 6
    return [(v,t,p),(q,v,p),(p,v,t),(p,q,v),(t,p,v),(v,p,q)][i]

""" Clase para seleccionar colores mediante una rueda de color HSV """
class ColorWheel:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        self.RenderWheel()
        self.selected = (255,255,255)
        self.selected_pos = (self.radius, self.radius)

    # Genera la rueda de color HSV
    def RenderWheel(self):
        cx = cy = self.radius
        for y in range(self.surface.get_height()):
            for x in range(self.surface.get_width()):
                dx, dy = x - cx, y - cy
                r = math.hypot(dx, dy)
                if r <= self.radius:
                    h = (math.degrees(math.atan2(dy, dx)) + 360) % 360 / 360.0
                    s = min(1.0, r / self.radius)
                    v = 1.0
                    self.surface.set_at((x,y), (*hsv_to_rgb(h,s,v), 255))
                else:
                    self.surface.set_at((x,y), (0,0,0,0))

    # Maneja eventos de clic para seleccionar un color
    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.GetRect().collidepoint(event.pos):
                x, y = event.pos[0]-self.GetRect().x, event.pos[1]-self.GetRect().y
                x = max(0, min(self.surface.get_width()-1, x))
                y = max(0, min(self.surface.get_height()-1, y))
                col = self.surface.get_at((x,y))
                if col.a != 0:
                    self.selected = (col.r, col.g, col.b)
                    # actualizar posición del marcador (local)
                    self.selected_pos = (x, y)

    # Dibuja la rueda y el marcador de selección
    def draw(self, s):
        s.blit(self.surface, self.GetRect())
    
        gx = self.GetRect().x + int(self.selected_pos[0])
        gy = self.GetRect().y + int(self.selected_pos[1])

        r,g,b = self.selected
        L = 0.2126*r + 0.7152*g + 0.0722*b
        border_color = (0,0,0) if L > 140 else (255,255,255)

        marker_outer_r = max(6, int(self.radius * 0.08))  # tamaño relativo
        marker_inner_r = max(4, marker_outer_r - 2)

        pygame.draw.circle(s, border_color, (gx, gy), marker_outer_r, width=2)
        pygame.draw.circle(s, self.selected, (gx, gy), marker_inner_r)

    # Obtiene el rectángulo que contiene la rueda
    def GetRect(self):
        return pygame.Rect(self.center[0]-self.radius, self.center[1]-self.radius, self.radius*2, self.radius*2)

    # Obtiene el color seleccionado en formato hexadecimal
    def hex(self):
        return "#{:02X}{:02X}{:02X}".format(*self.selected)

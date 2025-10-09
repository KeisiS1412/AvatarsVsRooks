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

class ColorWheel:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.surface = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        self._render_wheel()
        self.selected = (255,255,255)

    def _render_wheel(self):
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

    def handleEvent(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.get_rect().collidepoint(event.pos):
                x, y = event.pos[0]-self.get_rect().x, event.pos[1]-self.get_rect().y
                col = self.surface.get_at((x,y))
                if col.a != 0:
                    self.selected = (col.r, col.g, col.b)

    def draw(self, s):
        s.blit(self.surface, self.get_rect())

    def get_rect(self):
        return pygame.Rect(self.center[0]-self.radius, self.center[1]-self.radius, self.radius*2, self.radius*2)

    def hex(self):
        return "#{:02X}{:02X}{:02X}".format(*self.selected)

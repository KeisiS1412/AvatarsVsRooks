import pygame

def _clamp(x):
    if x < 0:
        return 0
    if x > 255:
        return 255
    return int(x)

def mul(c, k):
    r = _clamp(c[0] * k)
    g = _clamp(c[1] * k)
    b = _clamp(c[2] * k)
    return (r, g, b)

THEME_NAMES = ["Dark", "Default", "Bright"]
THEME_MULTS = [0.65, 1.00, 1.35]
DEFAULT_THEME_INDEX = 1

class Button:
    def __init__(self, x, y, width, height, text, font, normalColor=(200,200,200), hoverColor=(170,170,170), fontColor=(0,0,0)):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.text = text
        self.font = font
        self.normalColor = normalColor
        self.hoverColor = hoverColor
        self.currentColor = normalColor
        self.fontColor = fontColor
        self.textColor = fontColor
        self.on_click = None
        self.isHover = False

    def draw(self, screen, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        pygame.draw.rect(screen, self.currentColor, adjRect, border_radius=8)
        label = self.font.render(self.text, True, self.textColor)
        label_rect = label.get_rect(center=adjRect.center)
        screen.blit(label, label_rect)

    def update(self, mousePos, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        self.isHover = adjRect.collidepoint(mousePos)
        self.currentColor = self.hoverColor if self.isHover else self.normalColor

    def wasClicked(self, event, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and adjRect.collidepoint(event.pos)

class SimpleText:
    def __init__(self, text, centerX=0, centerY=0, font=None, textColor=(0, 0, 0), bgColor=None, padding=10):
        self.text = text
        self.font = font
        self.textColor = textColor
        self.bgColor = bgColor
        self.padding = padding
        self.label = self.font.render(self.text, True, self.textColor)
        self.rect = self.label.get_rect()
        self.rect.center = (centerX, centerY)
        if self.bgColor:
            self.rect.inflate_ip(self.padding * 2, self.padding * 2)

    def draw(self, screen, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        if self.bgColor:
            pygame.draw.rect(screen, self.bgColor, adjRect, border_radius=8)
        screen.blit(self.label, self.label.get_rect(center=adjRect.center))

    def wasClicked(self, event, scrollOffset=0):
        adjRect = self.rect.move(0, -scrollOffset)
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and adjRect.collidepoint(event.pos)

    def setText(self, newText):
        self.text = newText
        self.label = self.font.render(self.text, True, self.textColor)
        oldCenter = self.rect.center
        self.rect = self.label.get_rect()
        self.rect.center = oldCenter
        if self.bgColor:
            self.rect.inflate_ip(self.padding * 2, self.padding * 2)

    def update(self, deltaTime=0, scrollOffset=0):
        pass

class MainWindow:
    def __init__(self, font, res, switchSceneCallback, base_color=(30,120,200), theme_index=DEFAULT_THEME_INDEX):
        self.font = font
        self.res = res
        self.switchScene = switchSceneCallback
        self.buttons = []
        self.labels = []
        w, h = res
        self.content_w = min(800, int(w * 0.7))
        self.content_h = min(520, int(h * 0.7))
        self.content_x = (w - self.content_w) // 2
        self.content_y = (h - self.content_h) // 2
        self.theme_index = theme_index
        self.base_color = base_color
        self._recompute_palette()
        self.title = SimpleText("Demo: Tres Botones", centerX=w//2, centerY=self.content_y+60, font=self.font, textColor=self.fg)
        btn_w, btn_h, gap = 280, 64, 22
        start_y = self.content_y + 150
        x = self.content_x + (self.content_w - btn_w) // 2
        self.btn1 = Button(x, start_y + 0*(btn_h+gap), btn_w, btn_h, "Botón 1", font=self.font)
        self.btn2 = Button(x, start_y + 1*(btn_h+gap), btn_w, btn_h, "Botón 2", font=self.font)
        self.btn3 = Button(x, start_y + 2*(btn_h+gap), btn_w, btn_h, "Botón 3", font=self.font)
        self.buttons = [self.btn1, self.btn2, self.btn3]
        back_w, back_h = 120, 44
        self.btnBack = Button(self.content_x + 20, self.content_y + 20, back_w, back_h, "Volver", font=self.font)
        self.btn1.on_click = lambda: print("Botón 1 clicked")
        self.btn2.on_click = lambda: print("Botón 2 clicked")
        self.btn3.on_click = lambda: print("Botón 3 clicked")
        self.btnBack.on_click = lambda: self.switchScene("back") if self.switchScene else None
        self._apply_widget_colors()

    def _recompute_palette(self):
        if self.theme_index < 0 or self.theme_index >= len(THEME_MULTS):
            self.theme_index = DEFAULT_THEME_INDEX
        k = THEME_MULTS[self.theme_index]
        self.bg = mul(self.base_color, k)
        self.ui = mul(self.bg, 0.75)
        self.ui_border = mul(self.ui, 0.88)
        self.ui_hover = mul(self.ui, 0.82)
        self.ui_active = mul(self.ui, 0.70)
        L = 0.2126*self.ui[0] + 0.7152*self.ui[1] + 0.0722*self.ui[2]
        self.fg = (255, 255, 255) if L < 120 else (0, 0, 0)

    def set_theme(self, base_color=None, theme_index=None):
        if base_color is not None:
            self.base_color = base_color
        if theme_index is not None:
            self.theme_index = theme_index
        self._recompute_palette()
        self._apply_widget_colors()

    def _apply_widget_colors(self):
        self.panel_bg = self.ui
        self.panel_border = self.ui_border
        for b in self.buttons + [self.btnBack]:
            b.normalColor = self.ui
            b.hoverColor = self.ui_hover
            b.textColor = self.fg
            b.currentColor = b.normalColor

    def update(self, dt):
        pass

    def handle(self, event):
        for b in self.buttons + [self.btnBack]:
            b.update(pygame.mouse.get_pos())
            if b.wasClicked(event):
                if b.on_click:
                    b.on_click()

    def draw(self, s):
        s.fill(self.bg)
        pygame.draw.rect(s, self.panel_bg, (self.content_x, self.content_y, self.content_w, self.content_h), border_radius=18)
        pygame.draw.rect(s, self.panel_border, (self.content_x, self.content_y, self.content_w, self.content_h), width=2, border_radius=18)
        self.title.draw(s)
        for b in self.buttons + [self.btnBack]:
            b.draw(s)

    def on_enter(self, shared=None):
        if isinstance(shared, dict):
            self.set_theme(
                base_color=shared.get("base_color", self.base_color),
                theme_index=shared.get("theme_index", self.theme_index)
            )

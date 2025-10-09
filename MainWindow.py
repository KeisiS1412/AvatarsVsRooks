import pygame
from Scene import Scene
from Buttons import Button
from SimpleTexts import SimpleText


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


# Por defecto, usamos los 3 temas que definiste:
THEME_NAMES = ["Dark", "Default", "Bright"]
THEME_MULTS = [0.65, 1.00, 1.35]
DEFAULT_THEME_INDEX = 1


class MainWindow(Scene):
 

    def __init__(self, font, res, switchSceneCallback, base_color=(30,120,200), theme_index=DEFAULT_THEME_INDEX):
        self.font = font
        self.res = res
        self.switchScene = switchSceneCallback

        self.buttons = []
        self.labels = []

        # Layout básico
        w, h = res
        self.content_w = min(800, int(w * 0.7))
        self.content_h = min(520, int(h * 0.7))
        self.content_x = (w - self.content_w) // 2
        self.content_y = (h - self.content_h) // 2

        # Paleta inicial
        self.theme_index = theme_index
        self.base_color = base_color
        self._recompute_palette()

        # Título
        self.title = SimpleText("Demo: Tres Botones", size="lg")

        # Botones genéricos
        btn_w = 280
        btn_h = 64
        gap = 22
        start_y = self.content_y + 150
        x = self.content_x + (self.content_w - btn_w) // 2

        self.btn1 = Button(x, start_y + 0*(btn_h + gap), btn_w, btn_h, text="Botón 1", font=self.font)
        self.btn2 = Button(x, start_y + 1*(btn_h + gap), btn_w, btn_h, text="Botón 2", font=self.font)
        self.btn3 = Button(x, start_y + 2*(btn_h + gap), btn_w, btn_h, text="Botón 3", font=self.font)
        self.buttons = [self.btn1, self.btn2, self.btn3]

        
        back_w, back_h = 120, 44
        self.btnBack = Button(self.content_x + 20, self.content_y + 20, back_w, back_h, text="Volver", font=self.font)

       
        self.btn1.on_click = lambda: print("[GenericButtonsScene] Botón 1 clicked")
        self.btn2.on_click = lambda: print("[GenericButtonsScene] Botón 2 clicked")
        self.btn3.on_click = lambda: print("[GenericButtonsScene] Botón 3 clicked")
        self.btnBack.on_click = lambda: self.switchScene("back") if self.switchScene else None

        self._apply_widget_colors()

    def _recompute_palette(self):
        # Multiplicador de tema
        if self.theme_index < 0 or self.theme_index >= len(THEME_MULTS):
            self.theme_index = DEFAULT_THEME_INDEX
        k = THEME_MULTS[self.theme_index]

        # Fondo base con tema
        self.bg = mul(self.base_color, k)

        # Derivados (misma jerarquía de tonos que en tu UI)
        self.ui = mul(self.bg, 0.75)           # contenedores / tarjetas
        self.ui_border = mul(self.ui, 0.88)    # bordes sutiles
        self.ui_hover = mul(self.ui, 0.82)     # hover
        self.ui_active = mul(self.ui, 0.70)    # activo / presionado

        # Luz del texto 
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
            b.bg_color = self.ui
            b.text_color = self.fg
            b.border_color = self.ui_border
            b.hover_bg_color = self.ui_hover
            b.active_bg_color = self.ui_active

   
    def update(self, dt):
        pass

    def handle(self, event):
        for b in self.buttons:
            b.handle(event)
        self.btnBack.handle(event)

    def draw(self, s):
        s.fill(self.bg)


        pygame.draw.rect(s, self.panel_bg, (self.content_x, self.content_y, self.content_w, self.content_h), border_radius=18)
        pygame.draw.rect(s, self.panel_border, (self.content_x, self.content_y, self.content_w, self.content_h), width=2, border_radius=18)

        title_surface = self.title.render(self.font, color=self.fg)
        title_x = self.content_x + (self.content_w - title_surface.get_width()) // 2
        s.blit(title_surface, (title_x, self.content_y + 60))

        for b in self.buttons:
            b.draw(s)
        self.btnBack.draw(s)


    def on_enter(self, shared=None):
        """
        shared puede contener, por ejemplo:
        {
            "base_color": (r,g,b),
            "theme_index": int
        }
        """
        if isinstance(shared, dict):
            self.set_theme(
                base_color=shared.get("base_color", self.base_color),
                theme_index=shared.get("theme_index", self.theme_index)
            )

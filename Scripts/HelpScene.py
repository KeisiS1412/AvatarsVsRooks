import pygame
from Scene import Scene
from Buttons import Button
from LoginScene import LoginScene

class HelpScene(Scene):
    """Pantalla de ayuda de AvatarsVsRooks: explica controles, objetivos y mecánicas básicas."""

    def __init__(self, font, res, switchSceneCallback):
        super().__init__()
        self.font = font
        self.res = res
        self.switchSceneCallback = switchSceneCallback

        screenW, screenH = res
        self.centerX = screenW // 2

        # === Contenido del texto ===
        self.title_text = "AYUDA / INSTRUCCIONES"
        self.lines = [
            "Objetivo: Defiende tu base colocando torres elementales contra las hordas enemigas.",
            "Cada torre tiene un tipo y daño distinto: Fuego (10pts), Agua (12pts), Roca (8pts), Arena (6pts),",
            "además cada una tiene puntos de vida: Fuego 11pts, Agua 13pts, Roca 4pts y Arena 2pts.",
            "",
            "Controles básicos:",
            "  - Haz clic en una torre del panel que se encuentra a la derecha para seleccionarla.",
            "  - Luego haz clic en una celda del campo para colocarla.",
            "  - Las monedas se recolectan haciendo clic sobre ellas.",
            "  - Si una torre o avatar es destruido, desaparecerá del campo.",
            "",
            "Consejos:",
            "  - Usa combinaciones de elementos: algunos enemigos son más débiles ante ciertos tipos.",
            "  - Administra bien tus monedas: las torres más fuertes cuestan más.",
            "",
        ]

        # === Fuentes ===
        try:
            self.title_font = pygame.font.SysFont("arial", 80, bold=True)
        except Exception:
            self.title_font = self.font
        self.body_font = self.font

        # === Render del título y líneas ===
        self.title_surface = self.title_font.render(self.title_text, True, (255, 255, 255))
        self.body_surfaces = []
        y = 240
        for line in self.lines:
            surf = self.body_font.render(line, True, (255, 255, 255))
            self.body_surfaces.append((surf, y))
            y += 55

        # === Botón Volver ===
        self.back_btn = Button(
            self.centerX, screenH - 100,      # posición centrada horizontalmente
            300, 80,                          # tamaño
            "Volver al Login", self.body_font, # texto y fuente
            (0,0,0),                    # color normal
            (0, 0, 0),                   # color hover (no usado pero requerido)
            (255, 255, 255)                   # color del texto
        )

    # === Cambio de escena ===
    def _go_back(self):
        self.switchSceneCallback("login")

    # === Manejo de eventos ===
    def handleEvent(self, event):
        if self.back_btn.wasClicked(event):
            self._go_back()

    def update(self, dt):
        pass

    # === Dibujado ===
    def draw(self, screen):
        screen.fill((218, 41, 28))

        # Título centrado
        title_rect = self.title_surface.get_rect(center=(self.centerX, 120))
        screen.blit(self.title_surface, title_rect)

        # Texto cuerpo centrado
        for surf, y in self.body_surfaces:
            rect = surf.get_rect(center=(self.centerX, y))
            screen.blit(surf, rect)

        # Dibuja el botón
        self.back_btn.draw(screen)

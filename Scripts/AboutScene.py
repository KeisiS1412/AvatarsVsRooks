import pygame
from Scene import Scene
from Buttons import Button

class CreditsScene(Scene):
    """Pantalla de créditos de AvatarsVsRooks: muestra los desarrolladores y la empresa responsable."""

    def __init__(self, font, res, switchSceneCallback):
        super().__init__()
        self.font = font
        self.res = res
        self.switchSceneCallback = switchSceneCallback

        screenW, screenH = res
        self.centerX = screenW // 2

        # === Contenido del texto ===
        self.title_text = "CRÉDITOS"
        self.lines = [
            "Proyecto desarrollado por:",
            "",
            "Keisi Solano Ramírez",
            "Jose Manuel Chaves Chacón",
            "Daniel Ulate Solera",
            "Jose Ignacio Murillo Araya",
            "",
            "Empresa responsable:",
            "Byten S.A.",
            "",
            "© 2025 AvatarsVsRooks — Todos los derechos reservados."
        ]

        # === Fuentes ===
        try:
            self.title_font = pygame.font.SysFont("arial", 90, bold=True)
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
            y += 60

        # === Botón Volver ===
        self.back_btn = Button(
            self.centerX, screenH - 100,        # posición centrada
            300, 80,                            # tamaño
            "Volver al Login", self.body_font,  # texto y fuente
            (0, 0, 0),                          # color normal
            (50, 50, 50),                       # color hover (no usado pero requerido)
            (255, 255, 255)                     # color del texto
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
        screen.fill((218, 41, 28))  # rojo característico del juego

        # Título centrado
        title_rect = self.title_surface.get_rect(center=(self.centerX, 120))
        screen.blit(self.title_surface, title_rect)

        # Texto centrado
        for surf, y in self.body_surfaces:
            rect = surf.get_rect(center=(self.centerX, y))
            screen.blit(surf, rect)

        # Botón
        self.back_btn.draw(screen)

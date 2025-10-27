import pygame
from Scene import Scene
from Buttons import Button

class ModoJuegoScene(Scene):
    def __init__(self, font, res, switchSceneCallback):
        self.switchScene = switchSceneCallback
        self.font = font
        self.res = res

        screenW, screenH = res
        self.bg_color = (218, 41, 28)   # Rojo fondo

        # Botones
        button_w, button_h = 300, 60
        y_center = screenH // 2
        gap = 100

        x_positions = [
            screenW // 2 - button_w - gap,
            screenW // 2 - button_w // 2,
            screenW // 2 + gap
        ]

        labels = ["Fácil", "Medio", "Difícil"]
        self.buttons = []

        for i, label in enumerate(labels):
            btn = Button(
                x_positions[i], y_center,
                button_w, button_h,
                label, font,
                (20, 20, 20),        # fondo negro
                (255, 255, 255),     # texto blanco
                (255, 255, 255)      # borde blanco
            )
            self.buttons.append(btn)

    def handleEvent(self, event):
        for button in self.buttons:
            if button.wasClicked(event):
                print(f"Seleccionado modo: {button.text}")
                # Aquí luego harás self.switchScene("nombreDelModo") o similar

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mousePos)

    def draw(self, screen):
        screen.fill(self.bg_color)
        for button in self.buttons:
            button.draw(screen)

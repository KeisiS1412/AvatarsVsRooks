import pygame
from Scene import Scene
from Buttons import Button
from control.Cliente import Client


class GameModeScene(Scene):
    def __init__(self, font, res, switchSceneCallback, manager):
        self.switchScene = switchSceneCallback
        self.font = font
        self.res = res
        self.manager = manager
        screenW, screenH = res
        self.bg_color = (218, 41, 28)  # Fondo rojo

        # Botones de dificultad
        button_w, button_h = 300, 60
        spacing = 100
        y_center = screenH // 2

        labels = ["easy", "medium", "hard"]
        self.buttons = []
        self.conected = False

        # Calcular el ancho total de todos los botones más los espacios
        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = (screenW - total_width) // 2  # Centrado en la pantalla

        # Crear los botones centrados horizontalmente
        for i, label in enumerate(labels):
            x = start_x + i * (button_w + spacing) + button_w // 2
            btn = Button(
                x, y_center,
                button_w, button_h,
                label, font,
                (37, 32, 28),      # fondo oscuro
                (255, 255, 255),   # texto blanco
                (255, 255, 255)    # borde blanco
            )
            self.buttons.append(btn)

        # Botón de conectar centrado con el del medio
        medium_btn = self.buttons[1]
        connect_y = y_center + 200
        self.connectButton = Button(
            medium_btn.rect.centerx, connect_y,
            button_w, button_h,
            "Conectar control", font,
            (37, 32, 28),
            (255, 255, 255),
            (255, 255, 255)
        )

        # Cliente
        self.client = Client()

        # Fuente para el texto de estado
        self.status_font = pygame.font.Font(None, 36)

    def handleEvent(self, event):
        if self.conected:
            for button in self.buttons:
                if button.wasClicked(event):
                    if button.text == "easy":
                        self.manager.scenes["game"].setDifficulty("easy")
                    elif button.text == "medium":
                        self.manager.scenes["game"].setDifficulty("medium")
                    elif button.text == "hard":
                        self.manager.scenes["game"].setDifficulty("hard")

                    self.manager.scenes["game"].SetClient(self.client, self.conected)
                    self.switchScene("game")
        else:
            if self.connectButton.wasClicked(event):
                print("connect presionado")
                res = self.client.Connect()
                if res:
                    self.conected = True

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mousePos)
        self.connectButton.update(mousePos)

    def draw(self, screen):
        screen.fill(self.bg_color)

        # Dibujar botones
        for button in self.buttons:
            button.draw(screen)

        # Dibujar botón de conexión
        self.connectButton.draw(screen)

        # Mostrar texto de estado
        status_text = "Cliente conectado" if self.conected else "Cliente no conectado"
        color = (0, 255, 0) if self.conected else (255, 255, 255)
        status_surface = self.status_font.render(status_text, True, color)

        # Centrar texto debajo del botón de conectar
        status_rect = status_surface.get_rect(center=(
            self.connectButton.rect.centerx,
            self.connectButton.rect.bottom + 30
        ))
        screen.blit(status_surface, status_rect)

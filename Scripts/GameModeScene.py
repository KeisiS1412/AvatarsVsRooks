import pygame
from Scene import Scene
from Buttons import Button
from control.Cliente import Client


class GameModeScene(Scene):
    def __init__(self, font, res, switchSceneCallback, mananger):
        self.switchScene = switchSceneCallback
        self.font = font
        self.res = res
        self.manager = mananger
        screenW, screenH = res
        self.bg_color = (218, 41, 28)  # Rojo fondo
        # Botones
        button_w, button_h = 300, 60
        spacing = 100  # espacio entre botones
        y_center = screenH // 2

        labels = ["easy", "medium", "hard"]
        self.buttons = []
        self.conected = False

        # Ancho total ocupado por todos los botones + espacios
        total_width = len(labels) * button_w + (len(labels) - 1) * spacing
        start_x = (screenW - total_width) // 1.4

        for i, label in enumerate(labels):
            x = start_x + i * (button_w + spacing)
            btn = Button(
                x, y_center - button_h // 2,
                button_w, button_h,
                label, font,
                (37, 32, 28),      # fondo oscuro
                (255, 255, 255),   # texto blanco
                (255, 255, 255)    # borde blanco
            )
            self.buttons.append(btn)
        self.connectButton = Button(
                (screenW)//2+45, y_center - button_h // 2 +200,
                button_w, button_h,
                "Conectar control", font,
                (37, 32, 28),      # fondo oscuro
                (255, 255, 255),   # texto blanco
                (255, 255, 255)    # borde blanco
            )
        self.client = Client()

    def handleEvent(self, event):
        if self.conected:
            for button in self.buttons:
                if button.wasClicked(event):
                    if button.text == "easy":
                        self.manager.scenes["game"].setDifficulty("easy")
                        self.switchScene("game")
                    elif button.text == "medium":
                        self.manager.scenes["game"].setDifficulty("medium")
                        self.switchScene("game")
                    elif button.text == "hard":
                        self.manager.scenes["game"].setDifficulty("hard")
                        self.switchScene("game")
                    self.manager.scenes["game"].SetClient(self.client, self.conected)
        else:
            if self.connectButton.wasClicked(event):
                print("connect presionado")
                res = self.client.Connect()
                if res == True:
                    self.conected = True

    def update(self, deltaTime):
        mousePos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mousePos)
        self.connectButton.update(mousePos)

    def draw(self, screen):
        screen.fill(self.bg_color)
        for button in self.buttons:
            button.draw(screen)
        self.connectButton.draw(screen)


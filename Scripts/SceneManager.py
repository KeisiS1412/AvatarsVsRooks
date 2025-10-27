from LoginScene import LoginScene
from RegisterScene import RegisterScene
from AboutScene import AboutScene
from HelpScene import HelpScene
from GameModeScene import GameModeScene

class SceneManager:
    """Gestiona las diferentes escenas del juego y controla la escena activa."""

    def __init__(self, font, res):
        self.font = font
        self.res = res
        self.currentScene = None

        # Registra TODAS las escenas disponibles
        self.scenes = {
            "login": LoginScene(font, res, self.changeScene),
            "register": RegisterScene(font, res, self.changeScene),
            "About": AboutScene(font, res, self.changeScene),
            "Help": HelpScene(font, res, self.changeScene),
            "game_mode": GameModeScene(font, res, self.changeScene),  # ⬅️ NUEVA
        }

        # Escena inicial
        self.changeScene("login")

    def changeScene(self, name):
        if name not in self.scenes:
            raise ValueError(f"Escena '{name}' no registrada en SceneManager.")
        self.currentScene = self.scenes[name]

    def draw(self, screen):
        self.currentScene.draw(screen)

    def update(self, deltaTime):
        self.currentScene.update(deltaTime)

    def handleEvent(self, event):
        self.currentScene.handleEvent(event)

from LoginScene import LoginScene
from RegisterScene import RegisterScene
from AboutScene import AboutScene
from HelpScene import HelpScene


class SceneManager:
    """Gestiona las diferentes escenas del juego y controla la escena activa."""

    def __init__(self, font, res):  # Inicializa el administrador de escenas
        self.font = font
        self.currentScene = None
        self.scenes = {
            "login": LoginScene(font, res, self.changeScene),
            "register": RegisterScene(font, res, self.changeScene),
            "About": AboutScene(font, res, self.changeScene),
            "Help": HelpScene(font, res, self.changeScene)
        }
        self.changeScene("login")

    def changeScene(self, name):  # Cambia la escena actual
        self.currentScene = self.scenes[name]

    def draw(self, screen):  # Dibuja la escena actual
        self.currentScene.draw(screen)

    def update(self, deltaTime):  # Actualiza la escena actual
        self.currentScene.update(deltaTime)

    def handleEvent(self, event):  # Maneja los eventos en la escena actual
        self.currentScene.handleEvent(event)

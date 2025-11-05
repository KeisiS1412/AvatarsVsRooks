from LoginScene import LoginScene
from RegisterScene import RegisterScene
from AboutScene import CreditsScene
from HelpScene import HelpScene
from GameModeScene import GameModeScene
from recoverPasswordScene import recoverPasswordScene
from PersonalizationScene import PersonalizationScene

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
            "About": CreditsScene(font, res, self.changeScene),
            "Help": HelpScene(font, res, self.changeScene),
            "game_mode": GameModeScene(font, res, self.changeScene), 
            "recoverPassword" : recoverPasswordScene(font, res, self.changeScene),
            "personalization": PersonalizationScene(font, res, self.changeScene)
        }

        # Escena inicial
        self.changeScene("game_mode")

    def changeScene(self, name):
        self.currentScene = self.scenes[name]
        try:
            if hasattr(self.currentScene, "on_enter"):
                self.currentScene.on_enter()
            elif hasattr(self.currentScene, "refresh_user"):
                self.currentScene.refresh_user()
        except Exception:
            pass


    def draw(self, screen):
        self.currentScene.draw(screen)

    def update(self, deltaTime):
        self.currentScene.update(deltaTime)

    def handleEvent(self, event):
        self.currentScene.handleEvent(event)

from LoginScene import LoginScene
from RegisterScene import RegisterScene
from AboutScene import CreditsScene
from HelpScene import HelpScene
from GameModeScene import GameModeScene
from recoverPasswordScene import recoverPasswordScene
from PersonalizationScene import PersonalizationScene
from GameScene import GameScene
from FacialLoginScene import FacialLoginScene, FacialRegisterScene

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
            "game_mode": GameModeScene(font, res, self.changeScene, self), 
            "recoverPassword" : recoverPasswordScene(font, res, self.changeScene),
            "personalization": PersonalizationScene(font, res, self.changeScene),
            "game": GameScene(font, res, self.changeScene),
            "facial_login": FacialLoginScene(font, res, self.changeScene),
            "facial_register": FacialRegisterScene(font, res, self.changeScene),
        }

        # Escena inicial
        self.changeScene("game_mode")

    def changeScene(self, name):

        if name in self.scenes:
            self.currentScene = self.scenes[name]

        else:
            raise KeyError(f"Scene '{name}' not found")

        # Llamar on_scene_enter si existe
        if hasattr(self.currentScene, 'on_scene_enter'):
            try:
                self.currentScene.on_scene_enter()
            except Exception as e:
                print(f"Error en on_scene_enter: {e}")

    def draw(self, screen):
        self.currentScene.draw(screen)
        
    def update(self, deltaTime):
        self.currentScene.update(deltaTime)

    def handleEvent(self, event):
        self.currentScene.handleEvent(event)

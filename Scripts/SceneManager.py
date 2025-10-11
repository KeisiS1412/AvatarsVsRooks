from LoginScene import LoginScene
from RegisterScene import RegisterScene
from AboutScene import AboutScene
from HelpScene import HelpScene

class SceneManager:
    def __init__(self, font, res):
        self.font = font
        self.currentScene = None
        self.scenes = {
            "login": LoginScene(font, res, self.changeScene),
            "register": RegisterScene(font, res, self.changeScene),
            "About": AboutScene(font, res, self.changeScene),
            "Help": HelpScene(font, res, self.changeScene)
        }
        self.changeScene("login")

    def changeScene(self, name):
        self.currentScene = self.scenes[name]

    def draw(self, screen):
        self.currentScene.draw(screen)

    def update(self, deltaTime):
        self.currentScene.update(deltaTime)

    def handleEvent(self, event):
        self.currentScene.handleEvent(event)